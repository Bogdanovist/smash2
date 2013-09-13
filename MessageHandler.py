
class MessageHandler(set):
    
    def __init__(self,dt):
        self.dt = dt

    def add(self,msg):
        if msg.delay < 0.:
            self.process_message(msg)
        else:
            super(MessageHandler,self).add(msg)

    def process_message(self,msg):
        msg.to.get_message(msg)

    def process(self):
        for msg in self:
            msg.delay -= self.dt
            if msg.delay <= 0.:
                process_message(msg)

class Message(object):
    
    def __init__(self,to,sender,subject,body,delay=0.):
        """
        Default delay will result in delivery on the next check. Set to negative to send immediately.
        """
        self.to=to
        self.sender=sender
        self.subject=subject
        self.body=body
        self.delay=delay
