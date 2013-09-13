class State(object):
    """
    Base class for states
    """
    def __init__(self,owner):
        self.owner=owner
        self.messages=list()

    def enter(self):
        pass
    
    def execute(self):
        self.check_messages()

    def exit(self):
        pass

    def check_messages(self):
        if len(self.messages) > 0:
            for msg in self.messages:
                self.process_message(msg)

    def process_message(self,msg):
        pass

class StateMessage(dict):
    """
    Message passing to a state.
    """
    def __init__(self,subject,body):
        self['subject']=subject
        self['body']=body

