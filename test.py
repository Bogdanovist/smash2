from Pitch import *
from Player import *
from Team import * 
from MessageHandler import *
from Role import *

xsize=100.
ysize=50.
dt=0.1

message_handler=MessageHandler(dt)

pitch = Pitch(message_handler,xsize,ysize)

home=Team(message_handler,1)
away=Team(message_handler,-1)

utility=Role()

home1 = Player(message_handler,utility,pitch,25,25)

home.add_player(home1)

pitch.register_teams(home,away)
pitch.ball.pos = Vector(30,25)
pitch.run_game(10.,dt=dt)

