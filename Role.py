
class Role(object):
    """
    Defines the players role (or position). This is the strategic level of the player AI, that
    determines what States should be used in what circumstances.
    """
    def __init__(self,owner):
        self.owner=owner

    def get_message(self,msg,sender_id):
        """
        Only messages content looked at for the moment.
        """
        this=self.owner
        if msg == "ball_flying":
            this.state = PlayerBallFlying(self)
        elif msg == "ball_loose":
            this.state = PlayerBallLoose(self)
        elif msg == "ball_held":
            this.state = PlayerBallHeld(self)
        elif msg == "setup":
            this.setup()
        else:
            raise("Unknown message:" + msg + " recived")

class DefenderRole(Role):
    
    def get_message(self,msg,sender_id):
        """
        Only messages content looked at for the moment.
        """
        this=self.owner
        if msg == "ball_flying":
            this.state = PlayerBallFlying(self)
        elif msg == "ball_loose":
            this.state = PlayerBallLoose(self)
        elif msg == "ball_held":
            this.state = DefenderBallHeld(self)
        elif msg == "setup":
            this.setup()
        else:
            raise("Unknown message:" + msg + " recived")

