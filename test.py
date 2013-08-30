from Pitch import *
from Player import *
from Team import * 

xsize=100.
ysize=50.

pitch = Pitch(xsize,ysize)

home=Team(1)
away=Team(-1)

home1 = Player(pitch,45,45)
away1 = Player(pitch,90,40)
away2 = Player(pitch,80,40)
away3 = Player(pitch,70,40)

home.add_player(home1)
away.add_player(away1)
away.add_player(away2)
away.add_player(away3)


pitch.register_teams(home,away)
pitch.ball.pos = Vector(50,45)
pitch.run_game(5.)

