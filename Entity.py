from Vector import *
from MessageHandler import *

class Entity(object):
    """
    Base class for game entities.
    
    Sets up communication system.
    """
    def __init__(self,message_handler):
        self.uid=id(self)
        self.comms = list()
        self.pos = Vector(0,0)
        self.vel = Vector(0,0)
        self.message_handler=message_handler
        
    def register(self,obj):
        " Add a reciever for messages."
        self.comms.append(obj)

    def broadcast(self,subject,body=None,delay=None):
        " Send a message to all contacts."
        for c in self.comms:
            msg=Message(c,self,subject,body,delay)
            self.message_handler.add(msg)

    def send(self,to,subject,body,delay):
        " Send message to specific entity only."
        msg=Message(to,self,subject,body,delay)
        self.message_handler.add(msg)

    def get_message(self,msg):
        " Recieve a message."
        pass

    @property
    def state(self):
        return self._state
    @state.setter
    def state(self,new_state):
        try:
            self._state.exit()
        except:
            pass
        finally:
            self._state=new_state        
            self._state.enter()

    @property
    def x(self):
        return self.pos.x

    @property
    def y(self):
        return self.pos.y
