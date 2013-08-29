from Entity import *
from State import *
from Pitch import *
from Team import *
from Vector import *
from Steering import *
import pdb

class Player(Entity):
    """
    Player base class. Implements a general all-rounder position.
    """
    def __init__(self,pitch,xstart,ystart,top_speed=10.,acc=3.,strength=1.,throw_power=30.):
        Entity.__init__(self)
        self.pitch=pitch
        self.size=1.
        self.xstart=xstart
        self.ystart=ystart
        self.top_speed=top_speed
        self.top_acc=acc
        self.jerk=2.0 # m/s^3
        self.strength=strength
        self.throw_power=throw_power
        self.steering = Steering(self)
        # Experimental linear drag locamotion model
        self.drag = self.top_acc/self.top_speed
            
    def setup(self):
        """
        Call to reset to neutral state at starting position.
        """
        self.pos = Vector(self.xstart,self.ystart)
        self.vel = Vector(0.,0.)
        self.acc = Vector(0.,0.)
        self.standing=True
        self.prone=-1.
        ### Define how to resolve collisions between opposing team players
        # A player not wanting to block will instead try to evade, for instance
        # to get around a blocker to make a tackle, or get clear to make a lead
        # for a pass.
        self.want_to_block=True
        # Are we trying to catch the ball?
        self.want_to_catch=True
     
    def get_message(self,msg,sender_id):
        """
        Only messages content looked at for the moment.
        """
        if msg == "ball_flying":
            self.state = PlayerBallFlying(self)
        elif msg == "ball_loose":
            self.state = PlayerBallLoose(self)
        elif msg == "ball_held":
            self.state = PlayerBallHeld(self)
        elif msg == "setup":
            self.setup()
        else:
            raise("Unknown message:" + msg + " recived")
    
    @property
    def attack_end_zone_x(self):
        return self.team.attack_end_zone_x
    
    @property
    def defend_end_zone_x(self):
        return self.team.defend_end_zone_x

    @property
    def dist_to_attack_end_zone(self):
        return (self.attack_end_zone_x - self.x)*self.team.direction

    @property
    def dist_to_defend_end_zone(self):
        return (self.x - self.defend_end_zone_x)*self.team.direction

    @property
    def opposite_team(self):
        return self.team.opposite_team

    def move(self):
        # Don't move if we are prone
        if not self.standing:
            return

        desired_acc = self.state.execute().truncate(self.top_acc)
        # Apply jerk limit
        acc_diff = desired_acc - self.acc
        if acc_diff.mag() < self.jerk:
            acc_applied = desired_acc
        else:
            acc_applied = acc_diff.norm() * self.jerk
        # Apply drag
        drag = self.vel * self.drag
        self.vel += acc_applied - drag
        self.pos += self.vel * self.pitch.dt

    def standup(self):
        """
        Check if player is prone and if so whether they can stand yet.
        """
        if self.prone > 0.:
            self.prone -= self.pitch.dt
            if self.prone <= 0.:
                self.standing=True
            
class PlayerState(State):
    """
    Base class for Player states.
    """
    def execute(self):
        " Just resolve steering. "
        return self.owner.steering.resolve()   

    def exit(self):
        " Turn off all steering. "
        self.owner.steering.all_off()

class PlayerBallLoose(PlayerState):
    
    def enter(self):
        """
        Apply steering behaviours.
        """
        this=self.owner
        this.steering.seek_on(this.pitch.ball)

class PlayerBallHeld(PlayerState):
    
    def enter(self):
        this=self.owner
        if this.uid == this.pitch.ball.carrier:
            this.steering.seek_end_zone_on(this.attack_end_zone_x)
            this.steering.avoid_defenders_on(this.opposite_team)
        else:
            this.steering.seek_on(this.pitch.players[this.pitch.ball.carrier])
