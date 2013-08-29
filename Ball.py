from Entity import *
from Vector import *
from State import *
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
    def __init__(self,pitch):
        Entity.__init__(self)
        self.pitch=pitch
        self.state=BallLoose(self)
        self.pos = Vector(pitch.xsize/2,pitch.ysize/2.)
        self.carrier = None

    def move(self):
        self.state.execute()

class BallLoose(State):

    def enter(self):
        self.owner.broadcast('ball_loose')

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
                this.carrier = p.uid
                this.state = BallHeld(this)

class BallHeld(State):

    def enter(self):
        self.owner.broadcast('ball_held')

    def execute(self):
        """
        Move with ball carrier.
        """
        p = self.owner.pitch.players[self.owner.carrier]
        self.owner.pos = Vector(p.pos.x,p.pos.y)
