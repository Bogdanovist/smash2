from Vector import *

class Entity(object):
    """
    Base class for game entities.
    
    Sets up communication system.
    """
    def __init__(self):
        self.uid=id(self)
        self.comms = dict()
        self.pos = Vector(0,0)
        self.vel = Vector(0,0)
        
    def register(self,obj):
        " Add a reciever for messages."
        self.comms[obj.uid]=obj

    def broadcast(self,msg):
        " Send a message to all contacts."
        for c in self.comms.values():
            c.get_message(msg,self.uid)

    def send(self,msg,uid):
        " Send message to specific entity only."
        self.comms[uid].get_message(msg,self.uid)

    def get_message(self,msg,uid):
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
