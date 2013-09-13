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
        self.state=BallLoose(self)
        self.pos = Vector(pitch.xsize/2,pitch.ysize/2.)
        self.carrier = None

    def move(self):
        self.state.execute()

    def setup(self):
        self.pos = Vector(self.pitch.xsize/2,self.pitch.ysize/2.)
        self.carrier = None
        self.state = BallLoose(self)

    def get_message(self,msg):
        """
        Only messages content looked at for the moment.
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
            raise("Unknown message:" + msg.subject + " recived")
    
    def scatter_ball(self,amount):
        """
        Scatters the ball by up to amount in a random direction.
        """
        self.pos.x += np.random.random()*amount-amount/2.
        self.pos.y += np.random.random()*amount-amount/2.
        self.pos.x = Utils.bracket(0,self.pos.x,self.pitch.xsize)
        self.pos.y = Utils.bracket(0,self.pos.y,self.pitch.ysize)

class BallLoose(State):

    def enter(self):
        # Magic numbers
        scatter_amount=3.
        pdb.set_trace()
        self.owner.broadcast('ball_loose')
        self.owner.scatter_ball(scatter_amount)
        self.owner.carrier = None

    def execute(self):
        """
        Check for ball pickup.
        """
        this=self.owner
        # NOTE: Players could be over-lapping and close to ball, making who ends up with it random(ish).
        # BUT, if collision between players had been resolved first, maybe this is okay?
        
        for p in this.pitch.players.values():
            dist = (p.x - this.pos.x)**2 + (p.y - this.pos.y)**2
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
        self.owner.pos = Vector(p.pos.x,p.pos.y)
