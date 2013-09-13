from Entity import *
from State import *
from Player import *
import pdb

class Team(Entity):
    """
    A container for a team.
    """
    
    def __init__(self,message_handler,direction):
        """
        Direction sets the attack direction (via sign).
        """
        super(Team,self).__init__(message_handler)
        self.players=dict()
        self.direction=direction

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

    @property
    def in_possession(self):
        if self.pitch.ball.carrier.team == self:
            return True
        else:
            return False

    def add_player(self,p):
        self.players[p.uid] = p
        p.team=self
        # Add to contacts for message passing
        self.register(p)

    def get_message(self,msg):
        """
        Only message content looked at.
        """
        if msg.subject == "ball_flying":
            self.state = TeamBallFlying(self)
        elif msg.subject == "ball_loose":
            self.state = TeamBallLoose(self)
        elif msg.subject == "ball_held":
            self.state = TeamBallHeld(self)
        elif msg.subject == "setup":
            self.broadcast("setup",body=msg.body,delay=msg.delay)
        else:
            raise("Unknown message:" + msg.subject + " received")          

class TeamBallLoose(State):

    def enter(self):
        """
        Re-broadcast message to all players.
        """
        this=self.owner
        for p in this.players.values():
            p.broadcast('ball_loose')
        
class TeamBallHeld(State):
    
    def enter(self):
        """
        Re-broadcast message to all players.
        """
        # Magic numbers
        self.block_assignment_update_period = 1. # in seconds
        self.zone_defence_update_period = 1.
        this=self.owner
        for p in this.players.values():
            p.get_message('ball_held',this.uid)
        # We check for block regardless of being in attack or defence. We might want to maintain some blocking
        # when in defence for some reason.
        self.assign_blocks()
        self.block_update = self.block_assignment_update_period
        # As with blocking, check for zone defence in attack and defence.
        self.assign_zone_defence()
        self.zone_defence_update = self.zone_defence_update_period

    def execute(self):
        """
        Periodically re-assign blocking targets.
        """
        this=self.owner
        self.block_update -= this.pitch.dt
        self.zone_defence_update -= this.pitch.dt

        if self.block_update <= 0.:
            self.assign_blocks()
            self.block_update = self.block_assignment_update_period

        if self.zone_defence_update <= this.pitch.dt:
            self.assign_zone_defence()
            self.zone_defence_update = self.zone_defence_update_period

    def assign_blocks(self):
        this=self.owner
        bc=this.pitch.ball.carrier
        # Find all blockers
        blockers=list()
        # NOTE: Should do this (and the rest!) via list comprehensions (maybe?)
        for p in this.players.values():
            if p.steering._block_on: 
                blockers.append(p)
        # Find all standing defenders
        defenders=list()
        for p in this.opposite_team.players.values():
            if p.standing:
                defenders.append(p)
        # Find d2 for all defenders-BC
        dlist=list()
        for p in defenders:
            p._block_d2_temp = (p.pos-bc).mag2()
            dlist.append(p._block_d2_temp)
        while len(defenders) > 0 and len(blockers) > 0:
            # Find closest defender
            closest = defenders.pop(np.argmin(dlist))
            # Find nearest blocker
            blist=list()
            for p in blockers:
                blist.append( (p.pos-closest.pos).mag2())
            blocker = blockers.pop(np.argmin(blist))
            # Assign blocking target
            blocker.steering.block_target = closest
            # redo dlist
            dlist=list()
            for p in defenders:
                dlist.append(p._block_d2_temp)

    def assign_zone_defence(self):
        this=self.owner
        # NOTE: This implements a single defensive line. We could allow more fancy formations to be specified.
        # NOTE: Should probably use projections of positions instead of just current position.
                                     
        # find all zoners
        zoners=list()
        for p in this.players.values():
            if p.steering._zone_defend_on:
                zoners.append(p)
        # Find dy
        dy = this.pitch.ysize / ( len(zoners) + 1 )
        # NOTE: This should be done by sorting! This algo is dumb!
        i=1
        while len(zoners) > 0:
            yvals=list()
            for p in zoners:
                yvals.append(p.y)
            pnow = zoners.pop(np.argmin(yvals))
            # Assign y
            pnow.zone_defence_y_target = i*dy
