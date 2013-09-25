from Entity import *
from Vector import *
from State import *
import Utils
import pdb

class Ball(Entity):
    """
    Teh Ball.
    
    Can be in one of these states:
    * setup - setting up field
    * flying - in the air
    * loose - on ground or bouncing around
    * held - in hands
    """
    def __init__(self,message_handler,pitch):
        super(Ball,self).__init__(message_handler)
        self.pitch=pitch
        self.pos = Vector(pitch.xsize/2,pitch.ysize/2.)
        self.carrier = None
        # NOTE: Assume nominal height of 2 metres if not flying, for now.
        self.z = 2.
        self.vert_vel = Vector(0,0)
        # Magic Number
        self.g = -10.

    def move(self):
        self.state.execute()

    def setup(self):
        self.pos = Vector(self.pitch.xsize/2,self.pitch.ysize/2.)
        self.carrier = None
        self.state = BallLoose(self)

    def get_message(self,msg):
        """
        Only message content looked at for the moment.
        """
        if msg.subject == "ball_flying":
            self.state = BallFlying(self)
        elif msg.subject == "ball_loose":
            self.state = BallLoose(self)
        elif msg.subject == "ball_held":
            self.state = BallHeld(self)
        elif msg.subject == "setup":
            self.setup()
        else:
            raise Exception("Unknown message:" + msg.subject + " recived")
    
    def scatter_ball(self,amount):
        """
        Scatters the ball by up to amount in a random direction.
        """
        self.x += np.random.random()*amount-amount/2.
        self.y += np.random.random()*amount-amount/2.
        self.x = Utils.bracket(0,self.x,self.pitch.xsize)
        self.y = Utils.bracket(0,self.y,self.pitch.ysize)

    def launch(self,elv,power,target):
        """
        Initialise throw with given angle and power from current ball position.
        """
        # 'target' is location you want the ball to pass the nominal 2m of height at
        #  
        self.carrier=None
        self.z=2. # Assume passes start 2m off the ground.
        self.vel = (target-self.pos).norm()*power*math.cos(elv)
        self.vert_vel = power*math.sin(elv)
        self.target=target
        self.state=BallFlying(self)
        #dist = power**2 * math.sin(2.*elv)/self.g
        #dx, dy = utils.components(dist,self.angle)
        #self.xland = self.x + dx
        #self.yland = self.y + dy

    def catch_test(self,player):
        # NOTE: Implement modifier due to nearby opponents?
        # NOTE: Implement modifier based on velocity or something (i.e. short toss easy to catch)?
        return player.catch_skill > np.random.random()*100.

    def max_range_of(self,player):
        " Returns max range this player could pass "
        return -player.throw_power**2 / self.g

class BallLoose(State):

    def enter(self):
        # Magic numbers
        scatter_amount=3.
        self.owner.broadcast('ball_loose')
        self.owner.scatter_ball(scatter_amount)
        self.owner.carrier = None

    def execute(self):
        """
        Check for ball pickup.
        """
        this=self.owner
        # NOTE: Players could be over-lapping and close to ball, making who ends up with it random(ish).
        # BUT, if collision between players have been resolved first, maybe this is okay?
        
        for p in this.pitch.players.values():
            dist = (p.pos - this.pos).mag2()
            if dist < p.size**2:
                this.carrier = p
                this.state = BallHeld(this)

class BallHeld(State):

    def enter(self):
        self.owner.broadcast('ball_held')

    def execute(self):
        """
        Move with ball carrier.
        """
        p = self.owner.carrier
        self.owner.pos = Vector(p.x,p.y)

class BallFlying(State):
    
    def enter(self):
        self.owner.broadcast('ball_flying')
        
    def execute(self):
        " Iterate one flight tick "
        # Check for potential catchers
        # NOTE: Assume we can only catch if z <= 2 metres.
        # NOTE: Player heights and jumping??
        # Magic numbers
        catch_height=2.
        this = self.owner
        
        this.vert_vel += this.g * this.pitch.dt 
        znext = this.z + this.vert_vel*this.pitch.dt
        posnext = this.pos + this.vel* this.pitch.dt
        disp = posnext - this.pos

        if this.z <= catch_height:
            start = this.pos
        elif znext <= catch_height:
            # Find where ball passes catching height
            dmag = disp.mag()
            slope = (znext-this.z)/dmag
            start = -1*(this.z-catch_height)/dmag
        else:
            start = None
        
        caught_it=None
        if not start == None:
            # check for catch.
            caught_it=None
            catchers = [ p for p in this.pitch.players.values() if \
                             (p.pos - start).mag2() < p.size**2 or \
                             (p.pos - posnext).mag2() < p.size**2]
            if len(catchers) > 1:
                while len(catchers) > 0:
                    clist = [ (p.pos - start).mag2() for p in catchers ]
                    catcher = catchers.pop(np.argmin(clist))
                    if this.catch_test(catcher):
                        caught_it=catcher
                        catchers=list()   
            elif len(catchers) == 1:
                if this.catch_test(catchers[0]):
                    caught_it=catchers[0]
        
        if caught_it == None:
            this.pos = posnext
            this.z = znext
            # Check for out of bounds
            oob=False
            if this.x < 0:
                this.x = 0
                oob = True
            elif this.x > this.pitch.xsize:
                this.x = this.pitch.xsize
                oob = True
            if this.y < 0:
                this.y = 0
                oob = True
            elif this.y > this.pitch.ysize:
                this.y = this.pitch.ysize
                oob = True
            if oob:
                this.state = BallLoose(self)
                # NOTE: Simple wall like behaviour for OOB. What else to do?
            # Check for ball landing
            if this.z <= 0.:
                this.state = BallLoose(self)
        else:
            # Catch occured, change state as appropriate.
            this.state = BallHeld(self)
            # NOTE: Bit of a hack
            this.pos = caught_it.pos
