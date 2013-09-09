from Pitch import *
from Player import *
from Team import * 

xsize=100.
ysize=50.

pitch = Pitch(xsize,ysize)

home=Team(1)
away=Team(-1)

home1 = Player(pitch,25,25)
home2 = Player(pitch,45,15)
home3 = Player(pitch,45,25)
home4 = Player(pitch,45,35)
away1 = Player(pitch,80,10)
away2 = Player(pitch,80,27)
away3 = Player(pitch,80,41)

home.add_player(home1)
home.add_player(home2)
home.add_player(home3)
home.add_player(home4)
away.add_player(away1)
away.add_player(away2)
away.add_player(away3)


pitch.register_teams(home,away)
pitch.ball.pos = Vector(30,25)
pitch.run_game(10.)

