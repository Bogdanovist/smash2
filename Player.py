from Entity import *
from State import *
from Pitch import *
from Team import *
from Vector import *
from Steering import *
import Threat
import pdb

class Player(Entity):
    """
    Player base class. Implements a general all-rounder position.
    """
    def __init__(self,message_handler,role,pitch,xstart,ystart,top_speed=10.,acc=5.,strength=5.,throw_power=30.,\
                 stamina=100.,tough=100.,block_skill=5.,catch_skill=70.,mass=1.):
        super(Player,self).__init__(message_handler)
        self.role=role
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
        self._health = self.tough 
        self._state = None

    def setup(self):
        """
        Call to reset to neutral state at starting position.
        """
        self.pos = Vector(self.xstart,self.ystart)
        self.vel = Vector(0.,0.)
        self.acc = Vector(0.,0.)
        self.standing=True
        self._prone=-1.
        # Are we trying to catch the ball?
        self.want_to_catch=True
        self._state=None

    @property
    def prone(self):
        return self._prone
    
    @prone.setter
    def prone(self,value):
        if value < 0.:
            self.standing = True
        else:
            self.standing = False
            if self.has_ball:
                self.drop_ball()
            if self.in_contact:
                self.pitch.remove_all_contact(self)
        self._prone=value
    
    @property
    def health(self):
        return self._health

    @health.setter
    def health(self,value):
        if value < 0.:
            msg = (self.team,self,'tap_out')
            self.message_handler.add(msg)

    def get_message(self,msg):
        """
        Only messages content looked at for the moment.
        """

        if msg.subject == "ball_flying":
            self.state = self.role['ball_flying'](self)
        elif msg.subject == "ball_loose":
            self.state = self.role['ball_loose'](self)
        elif msg.subject == "ball_held":
            if self.has_ball:
                self.state = self.role['ball_carrier'](self)
            elif self.team_in_possession:
                self.state = self.role['attack'](self)
            else:
                self.state = self.role['defence'](self)
        elif msg.subject == "setup":
            self.setup()
        else:
            if not self.state.get_message(msg):
                print("Uncaught message " + msg.subject)    
                #raise Exception("Unknown message:" + msg.subject + " recived")
    
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

    @property
    def has_ball(self):
        return self.pitch.ball.carrier == self

    @property
    def in_contact(self):
        return self in self.pitch.contacts.keys()

    @property
    def team_name(self):
        if self.team.direction > 0:
            return('home')
        else:
            return('away')

    @property
    def team_in_possession(self):
        return self.team.in_possession

    def x_from_defend_end_zone(self,x):
        if self.team.direction > 0:
            return x
        else:
            return self.pitch.xsize-x  

    def move(self):
        # Don't move if we are prone
        # NOTE: Ignores mass! (assumes m=1 I guess)
        if not self.standing:
            # Prone players might still be moving, but they rapidly deccelerate!
            # Magic numbers
            prone_acc = 20.
            prone_top_speed = 5.
            desired_acc = self.vel.norm() * prone_acc * self.pitch.dt * -1.
            if self.vel.mag() < desired_acc.mag():
                self.vel=Vector(0,0)
            else:
                self.vel += desired_acc
                self.vel = self.vel.truncate(prone_top_speed)
                self.pos += self.vel * self.pitch.dt
            return
        elif self.in_contact:
            # Push resolved seperately
            return
        acc = self.current_acc()
        # Check current puff reduced acc
        desired_acc = self.state.execute().truncate(acc)
        self.vel += desired_acc * self.pitch.dt
        self.vel = self.vel.truncate(self.top_speed)
        self.pos += self.vel * self.pitch.dt
        # It costs puff to move
        self.puff -= desired_acc.mag() * self.pitch.dt * self.pitch.puff_fac

    def push(self):
        if not self.in_contact: return
        # NOTE: Pushing forwards always, but we don't always want to do that. Need to have hook
        # into state and define in states the push directions ( a parrallel steering behaviours).
        
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
        # Done via property now (but is it working?)
        #if self.prone > 0.:
        self.prone -= self.pitch.dt
        #    if self.prone <= 0.:
        #        self.standing=True
    
    def drop_ball(self):
        self.send(self.pitch.ball,'ball_loose')
        
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

class PlayerBallCarrier(PlayerState):    
    def enter(self):
        this=self.owner
        this.steering.seek_end_zone_on(this.attack_end_zone_x)
        this.steering.avoid_defenders_on(this.opposite_team)
        this.steering.avoid_walls_on(this.pitch)
    
    def execute(self):
        # Check for pass
        # NOTE: Checks all friends, including Blockers?
        this = self.owner
        max_range2 = this.pitch.ball.max_range_of(this)**2

        recs = [ p in this.team.players.values() if p.standing and (p.pos - this.pos).mag2() < max_range2 ]
        threats = [ Threat.rx_threat(rx) for rx in recs ]
        imin = np.argmin(threats)
        best_threat = threats[imin]

        my_threat = Threat.bc_threat(this)
        
        #NOTE: Doesn't take into account extra risk from pass, will lead to lots of passing.
        if my_threat > best_threat:
            # Make a pass
            
        return super(PlayerBallCarrier,self).execute()

class PlayerDefence(PlayerState):
    def enter(self):
        this=self.owner
        this.steering.pursue_on(this.pitch.ball.carrier)
        this.steering.avoid_friends_on(this.team)

class PlayerBallFlying(PlayerState):
    pass

class DefenderBallLoose(PlayerState):
    pass

class DefenderBallFlying(PlayerState):
    pass

class DefenderDefence(PlayerState):

    def enter(self):
        this=self.owner
        #this.steering.zone_defend_on()

    def execute(self):
        # Check if defensive target has been knocked over
        this=self.owner
        if this.steering._pursue_on:
            if not this.steering.pursue_target.standing:
                msg=Message(this.team,this,'defensive_target_down')
                this.message_handler.add(msg)
                # This turns default no target steering back on, then resolves steering
                self.exit()
                self.enter()
        return super(DefenderDefence,self).execute()
    
    def get_message(self,msg):
        this=self.owner
        if msg.subject == 'defensive_target':
            target = msg.body
            this.steering.all_off()
            this.steering.pursue_on(target)
            return True
        else:
            return False

class DefenderAttack(PlayerState):
    def enter(self):
        this=self.owner
        this.steering.pursue_on(this.pitch.ball.carrier)
        this.steering.avoid_friends_on(this.team)

class BlockerAttack(PlayerState):
    def enter(self):
        this=self.owner
        this.steering.guard_on(this.pitch.ball.carrier)
        this.steering.avoid_friends_on(this.team)

    def execute(self):
        # Check if any blocking target has been knocked over
        this=self.owner
        if this.steering._block_on:
            if not this.steering.block_target.standing:
                msg=Message(this.team,this,'block_target_down')
                this.message_handler.add(msg)
                # Exit then re-enter to turn back on no target behaviour
                self.exit()
                self.enter()
        # call super method to resolve steering
        return super(BlockerAttack,self).execute()

    def get_message(self,msg):
        this=self.owner
        if msg.subject == 'block_target':
            block_target, block_protect = msg.body
            this.steering.block_on(block_target,block_protect)
            this.steering.guard_off()
            return True
        else:
            return False

class BlockerDefence(PlayerState):
    pass

class RxBallFlying(PlayerState):
    pass

class RxAttack(PlayerState):

    def enter(self):
        # Magic numbers below
        this=self.owner
        this.steering.seek_end_zone_on(this.attack_end_zone_x)
        this.steering.avoid_defenders_on(this.opposite_team)
        this.steering.avoid_walls_on(this.pitch)
        this.steering.avoid_friends_on(this.team,ignore_dist=10)
        bc_range = this.pitch.ball.max_range_of(this.pitch.ball.carrier)
        this.steering.stay_in_range_on(this.pitch.ball.carrier,\
                                           max_range=bc_range*0.8,ignore_dist=bc_range*0.4)
        this.steering.avoid_end_zone_on(this.attack_end_zone_x)

