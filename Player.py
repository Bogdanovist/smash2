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
    def __init__(self,pitch,xstart,ystart,top_speed=10.,acc=3.,strength=1.,throw_power=30.,\
                 stamina=100.,tough=100.,block_skill=50.,mass=1.):
        Entity.__init__(self)
        self.pitch=pitch
        self.size=1.
        self.xstart=xstart
        self.ystart=ystart
        self.top_speed=top_speed
        self.top_acc=acc
        self.stamina=stamina
        self.tough=tough
        self.strength=strength
        self.throw_power=throw_power
        self.block_skill=block_skill
        self.mass=mass
        self.steering = Steering(self)
        # Experimental linear drag locomotion model
        self.drag = self.top_acc/self.top_speed
        # Damage and exhaustion counters
        self.puff = self.stamina
        self.health = self.tough 

    def setup(self):
        """
        Call to reset to neutral state at starting position.
        """
        self.pos = Vector(self.xstart,self.ystart)
        self.vel = Vector(0.,0.)
        self.acc = Vector(0.,0.)
        self.standing=True
        self.prone=-1.
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

    @property
    def direction(self):
        return self.team.direction    

    def move(self):
        # Don't move if we are prone
        # NOTE: Ignores mass! (assumes m=1 I guess)
        if not self.standing:
            return
        acc = self.current_acc()
        # Check current puff reduced acc
        desired_acc = self.state.execute().truncate(acc)
        self.vel += desired_acc
        self.vel.truncate(self.top_speed)
        self.pos += self.vel * self.pitch.dt
        # It costs puff to move
        self.puff -= desired_acc.mag() * self.pitch.dt * self.pitch.puff_fac
        print(self.puff)

    def current_acc(self):
        " Current puff reduced max accel."
        cut_in=0.5
        ability_floor=0.5
        # Reduce ability linearily after cut in, down to floor
        ratio = self.puff/self.stamina
        if ratio < cut_in:
            fac = ratio*(1.-ability_floor)/cut_in + ability_floor
        else:
            fac = 1.
        return fac*self.top_acc

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
            this.steering.avoid_walls_on(this.pitch)
        else:
            this.steering.pursue_on(this.pitch.players[this.pitch.ball.carrier])
