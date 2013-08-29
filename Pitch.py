from Entity import *
from Ball import * 
import pdb
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import json

class Pitch(Entity):
    """
    Manager class holding both teams and the ball. Runs the game.
    """
    def __init__(self,xsize,ysize):
        self.xsize=float(xsize)
        self.ysize=float(ysize)       
        self.ball=Ball(self)
        self.moves=list()

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
        # Run it
        nsteps=int(game_length/self.dt)
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
        #self.detect_collisions()
        #self.resolve_collisions()
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
