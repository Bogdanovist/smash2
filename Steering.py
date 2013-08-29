import numpy as np
import scipy as sp
from Vector import *
import pdb

class Target(object):
    """
    Provides interface identical to players in order to use steering behaviours
    for non-player locations or players seamlessly.
    """
    def __init__(self,pos,vel):
        self.pos=pos
        self.vel=vel

class Steering(object):
    """
    Implements steering behaviours. Behaviours all return a vector indicating the direction
    that acceleration should be applied.
    """
    def __init__(self,player):
        self.priority=list()
        self.player=player
        self._seek_on=False
        self._seek_end_zone_on=False
        self._avoid_defenders_on=False

    def seek_on(self,target,w=1.):
        self.seek_target=target
        self._seek_on=True
        self.w_seek=w

    def seek_off(self):
        self._seek_on=False

    def seek_end_zone_on(self,target,w=1.):
        self.seek_end_zone_target=target
        self._seek_end_zone_on=True
        self.w_seek_end_zone=w

    def seek_end_zone_off(self):
        self._seek_end_zone_on=False    

    def avoid_defenders_on(self,team,w=1.):
        self._avoid_defenders_on = True
        self.w_avoid_defenders=w
        self.avoid_defenders_team=team

    def avoid_defenders_off(self):
        self._avoid_defenders_on=False

    def all_off(self):
        self.seek_off()
        self.seek_end_zone_off()
        self.avoid_defenders_off()

    def resolve(self):
        """
        Return combined result of all steering behaviours.
        Uses weighted average truncated with priority order.
        NOTE: Currently can't change priority order. Is that a problem?
        """
        acc=Vector(0,0)
        if self._avoid_defenders_on:
            acc += self.avoid_defenders() * self.w_avoid_defenders
            #if acc.mag() >= self.player.acc:
            #    return acc
        if self._seek_on:
            acc += self.seek() * self.w_seek
            #if acc.mag() >= self.player.acc:
            #    return acc
        if self._seek_end_zone_on:
            acc += self.seek_end_zone() * self.w_seek_end_zone
            #if acc.mag() >= self.player.acc:
            #    return acc
        if self._avoid_defenders_on:
            print(self.avoid_defenders().mag(),self.seek_end_zone().mag(),acc.mag(),acc.x,acc.y)
        return acc

    def seek(self):
        """
        Attempts to acc directly at target.
        """
        desired_velocity = (self.seek_target.pos-self.player.pos).norm() * self.player.top_speed
        return (desired_velocity - self.player.vel).norm() * self.player.top_acc
        
    def seek_end_zone(self):
        """
        Attempts to acc directly at an end zone denoted by its x value (no y value needed).
        """
        desired_x_velocity = np.sign(self.seek_end_zone_target-self.player.x) * self.player.top_speed
        return (Vector(desired_x_velocity,0.) - self.player.vel).norm() * self.player.top_acc
    
    def avoid_defenders(self):
        """
        Avoid just the nearest defender by acc directly away from them.
        Ignores anyone not goalward of us, even if they are close and faster than us.
        """
        this=self.player
        ignore_dist=30.
        panic_dist=5.
        #
        nearest=None
        nearest_dist2 = 1e10
        ignore_dist2=ignore_dist**2
        this_end_zone_dist = this.dist_to_attack_end_zone
        for p in self.avoid_defenders_team.players.values():
            if this_end_zone_dist < p.dist_to_defend_end_zone : continue
            dist2 = (this.pos - p.pos).mag2()
            if dist2 < nearest_dist2:
                nearest=p
                nearest_dist2=dist2
        if nearest == None:
            return Vector(0,0)
        if nearest_dist2 > ignore_dist2:
            return Vector(0,0)
        else:
            # Calculate distance scaling
            dist = np.sqrt(nearest_dist2)
            if dist <= panic_dist:
                fac=1.
            else:
                fac = 1.-(dist-panic_dist)/(ignore_dist-panic_dist)
            desired_velocity = (this.pos-nearest.pos).truncate(self.player.top_speed)
            return (desired_velocity - self.player.vel).truncate(self.player.top_acc)*fac

