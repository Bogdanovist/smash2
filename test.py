from Pitch import *
from Player import *
from Team import * 
from MessageHandler import *
from Role import *
import pdb

xsize=100.
ysize=50.
dt=0.1

message_handler=MessageHandler(dt)

pitch = Pitch(message_handler,xsize,ysize)

home=Team(message_handler,1)
away=Team(message_handler,-1)

utility=Role()
blocker=BlockerRole()
rx=RxRole()
defender=DefenderRole()

home1 = Player(message_handler,utility,pitch,50,25)
home2 = Player(message_handler,blocker,pitch,70,15)
home3 = Player(message_handler,blocker,pitch,70,27)
home4 = Player(message_handler,blocker,pitch,70,35)
home5 = Player(message_handler,rx,pitch,80,45)

away1 = Player(message_handler,utility,pitch,90,10)
away2 = Player(message_handler,utility,pitch,90,20)
away3 = Player(message_handler,utility,pitch,90,30)
away4 = Player(message_handler,utility,pitch,90,40)
away5 = Player(message_handler,defender,pitch,90,40)

home.add_player(home1)
home.add_player(home2)
home.add_player(home3)
home.add_player(home4)
home.add_player(home5)

away.add_player(away1)
away.add_player(away2)
away.add_player(away3)
away.add_player(away4)
away.add_player(away5)

pitch.register_teams(home,away)
pitch.run_game(20.,dt=dt)

