from Entity import *
from Ball import * 
import pdb
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import json
import itertools
import random

class Pitch(Entity):
    """
    Manager class holding both teams and the ball. Runs the game.
    """
    def __init__(self,xsize,ysize,puff_fac=1.,damage_fac=1.):
        self.xsize=float(xsize)
        self.ysize=float(ysize)       
        self.ball=Ball(self)
        self.moves=list()
        self.puff_fac=puff_fac
        self.damage_fac=damage_fac

    def register_teams(self,home,away):
        self.home=home
        self.away=away
        home.pitch=self
        away.pitch=self
        home.opposite_team=away
        away.opposite_team=home
        self.players=dict()
        for p in home.players.values():
            self.players[p.uid]=p
        for p in away.players.values():
            self.players[p.uid]=p
        # Register teams to the Ball
        self.ball.register(self.home)
        self.ball.register(self.away)    

    def run_game(self,game_length,dt=0.1,display=True):
        " Run the game "
        self.display=display
        self.dt=dt
        # Setup move storage
        self.player_header=dict()
        for p in self.home.players.values():
            self.player_header[p.uid]=make_player_dict(1,'null')
        for p in self.away.players.values():
            self.player_header[p.uid]=make_player_dict(-1,'null')            
        # Add ball to player_header
        self.player_header[self.ball.uid]=make_player_dict(0,'null')
        # Init player states using a ball state broadcast
        self.ball.broadcast('setup')
        self.ball.state=BallLoose(self.ball)
        if display:
            fig1=plt.figure()
            plt.xlim([0,self.xsize])
            plt.ylim([0,self.ysize])
            self.plots=list()
            for p in self.home.players.values():
                plot_now, = plt.plot([], [], 'ro',markersize=15)
                self.plots.append(plot_now)
            for p in self.away.players.values():
                plot_now, = plt.plot([], [], 'bo',markersize=15)
                self.plots.append(plot_now)
            plot_now, =  plt.plot([],[],'go')
            self.plots.append(plot_now)
        # Run it
        nsteps=int(game_length/self.dt) 
        for i in range(nsteps):
            self.tick()
        # Dump to JSON
        jfile = "/home/matt/src/smash/games/test_header.js"
        with open(jfile,'w') as f:
            f.write(json.dumps(self.player_header))
        jfile = "/home/matt/src/smash/games/test.js"
        with open(jfile,'w') as f:
            f.write(json.dumps(self.moves))        
        if display:
            line_ani = animation.FuncAnimation(fig1,self.frame_display,self.frame_data,interval=20,blit=False,repeat=True)
            plt.show()

    def tick(self):
        """
        Iterate one tick.
        """
        # Stand prone players up
        for p in self.players.values():
            p.standup()
        # Move all players
        for p in self.players.values():
            p.move()
        self.detect_collisions()
        self.resolve_collisions()
        self.ball.move()
        # Store moves
        tick_moves=list()
        for p in self.players.values():
            have_ball = p.uid == self.ball.carrier
            add_move=make_move_dict(p.uid,p.pos.x,p.pos.y,0.,have_ball,int(p.standing))
            tick_moves.append(add_move)
        # Ball position,use pid=0 for ball
        ball_carried = self.ball.carrier != 0
        add_move=make_move_dict(self.ball.uid,self.ball.pos.x,self.ball.pos.y,0,ball_carried,0)
        tick_moves.append(add_move)
        #
        self.moves.append(tick_moves)
        # Display results
        if self.display:
            self.frame_display(tick_moves)
            plt.show(block=False)

    def detect_collisions(self):
        self.collisions=list()
        for this,that in itertools.combinations(self.players.values(),2):
            if not (this.standing and that.standing):
                # Prone players can be run over
                continue
            else:
                if (this.pos - that.pos).mag2() - (this.size + that.size)**2 < 0:
                    # collision occured
                    collision = this, that
                    self.collisions.append(collision)

    def resolve_collisions(self):
        for c in self.collisions:
            this, that = c[0]
            if this.team == that.team:
                # NOTE: For now, ignore friendly collisions.
                continue
            else:
                # Opposing team players. Game on.
                # Find elasticity factor, runs from [0,1]
                elasticity= (this.pos.angle_factor(that.pos)+1)/2.
                centre_of_mass=(this.pos*this.mass + that.pos*that.mass)/2.
                # Compute initial momentum, including additional pushes.
                p_before = this.vel * this.mass + that.vel * that.mass + \
                    this.strength*random.random()*this.vel.norm() + \
                    that.strength*random.random()*that.vel.norm()







    def frame_data(self):
        nticks=len(self.moves)
        iframe=0
        while iframe < nticks:
            moves=self.moves[iframe]
            iframe = iframe + 1
            yield moves

    def frame_display(self,frame_data):
        for move, p in zip(frame_data,self.plots):
            if move['state'] == 0:
                shape='v'
            else:
                shape='o'

            if self.player_header[move['uid']]['team'] == 1:
                col='r'
            elif self.player_header[move['uid']]['team'] == -1:
                col='b'
            else:
                col='g'
                shape='o'
            p.set_data(move['x'],move['y'])
            p.set_marker(shape)
            p.set_color(col)

def make_move_dict(uid,x,y,angle,have_ball,state):
    """
    Utility function to make a small dictionary to store a single move.
    """
    return dict(zip(['uid','x','y','angle','have_ball','state'],[uid,x,y,angle,have_ball,state]))

def make_player_dict(team,position):
    """
    Utility function for making player data as a small dict
    """
    return dict(zip(['team','position'],[team,position]))
