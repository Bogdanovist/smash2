from Pitch import *
from Player import *
from Team import * 

xsize=100.
ysize=50.

pitch = Pitch(xsize,ysize)

home=Team(1)
away=Team(-1)

home1 = Player(pitch,45,25)
away1 = Player(pitch,90,10)

home.add_player(home1)
away.add_player(away1)

pitch.register_teams(home,away)

pitch.run_game(5.)

