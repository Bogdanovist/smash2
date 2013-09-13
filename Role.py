from Player import *
"""
Different roles implemented as different class for conveniance. However, they details are actually all
just softcoded in the self.config dictionary. This allows easier configuration from info stored as set
by the manager.
"""

class Role(dict):
    """
    Defines the players role (or position). This is the strategic level of the player AI, that
    determines what States should be used in what different ball states.
    """
    def __init__(self):
        self.update([ ('ball_loose',PlayerBallLoose),\
                                 ('ball_flying',PlayerBallFlying),\
                                 ('ball_carrier',PlayerBallCarrier),\
                                 ('defence',PlayerDefence),\
                                 ('attack',PlayerAttack)])

class DefenderRole(Role):
    def __init__(self):
        self.update([ ('ball_loose',DefenderBallLoose),\
                                 ('ball_flying',DefenderBallFlying),\
                                 ('ball_carrier',PlayerBallCarrier),\
                                 ('defence',DefenderDefence),\
                                 ('attack',DefenderAttack)])
