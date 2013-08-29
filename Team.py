from Entity import *
from State import *
import pdb

class Team(Entity):
    """
    A container for a team.
    """
    
    def __init__(self,direction):
        """
        Direction sets the attack direction (via sign).
        """
        self.players=dict()
        self.direction=direction
        Entity.__init__(self)

    @property
    def attack_end_zone_x(self):
        if self.direction > 0.:
            return self.pitch.xsize
        else:
            return 0.

    @property
    def defend_end_zone_x(self):
        if self.direction > 0.:
            return 0.
        else:
            return self.pitch.xsize

    def add_player(self,p):
        self.players[p.uid] = p
        p.team=self
        # Add to contacts for message passing
        self.register(p)

    def get_message(self,msg,sender_id):
        """
        Only message content looked at.
        """
        if msg == "ball_flying":
            self.state = TeamBallFlying(self)
        elif msg == "ball_loose":
            self.state = TeamBallLoose(self)
        elif msg == "ball_held":
            self.state = TeamBallHeld(self)
        elif msg == "setup":
            self.broadcast("setup")
        else:
            raise("Unknown message:" + msg + " received")          

class TeamBallLoose(State):

    def enter(self):
        """
        Re-broadcast message to all players.
        """
        this=self.owner
        for p in this.players.values():
            p.get_message('ball_loose',this.uid)
        
class TeamBallHeld(State):
    
    def enter(self):
        """
        Re-broadcast message to all players.
        """
        this=self.owner
        for p in this.players.values():
            p.get_message('ball_held',this.uid)
