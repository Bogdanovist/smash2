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
        self._avoid_walls_on=False
        self._pursue_on=False
        self._block_on=False
        self._avoid_friends_on=False
        self._zone_defend_on=False

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

    def avoid_walls_on(self,pitch,w=1.):
        self._avoid_walls_on = True
        self.w_avoid_walls=w
        self.avoid_walls_pitch=pitch

    def avoid_walls_off(self):
        self._avoid_walls_on = False

    def pursue_on(self,target,w=1.):
        self._pursue_on = True
        self.w_pursue=w
        self.pursue_target=target
        
    def pursue_off(self):
        self._pursue_on = False

    def block_on(self,w=1.):
        self._block_on = True
        self.w_block=w
        self.block_carrier=self.player.pitch.ball.carrier
        self.block_team=self.player.team
        self.block_target=None # will be assinged by the Team

    def block_off(self):
        self._block_on = False

    def avoid_friends_on(self,team,w=1.):
        self._avoid_friends_on = True
        self.w_avoid_friends=w
        self.avoid_friends_team=team

    def avoid_friends_off(self):
        self._avoid_friends_on=False

    def zone_defend_on(self,w=1.):
        self._zone_defend_on=True
        self.w_zone_defend=w
        self.zone_defend_team = self.owner.team

    def zone_defend_off(self):
        self._zone_defend_on=False

    def all_off(self):
        self.seek_off()
        self.seek_end_zone_off()
        self.avoid_defenders_off()
        self.avoid_walls_off()
        self.pursue_off()
        self.block_off()
        self.avoid_friends_off()
        self.zone_defend_off()

    def resolve(self):
        """
        Return combined result of all steering behaviours.
        """
        acc=Vector(0,0)
        if self._avoid_defenders_on:
            acc += self.avoid_defenders() * self.w_avoid_defenders
        if self._seek_on:
            acc += self.seek() * self.w_seek
        if self._seek_end_zone_on:
            acc += self.seek_end_zone() * self.w_seek_end_zone
        if self._avoid_walls_on:
            acc += self.avoid_walls() * self.w_avoid_walls
        if self._pursue_on:
            acc += self.pursue() * self.w_pursue
        if self._block_on:
            acc += self.block() * self.w_block
        if self._avoid_friends_on:
            acc += self.avoid_friends() * self.w_avoid_friends
        if self._zone_defend_on:
            acc += self.zone_defend() * self.w_zone_defend
        return acc.truncate(self.player.top_acc)

    def seek(self):
        """
        Attempts to acc directly at target.
        """
        desired_velocity = (self.seek_target.pos-self.player.pos).norm() * self.player.top_speed
        return (desired_velocity - self.player.vel)
        
    def seek_end_zone(self):
        """
        Attempts to acc directly at an end zone denoted by its x value (no y value needed).
        """
        desired_x_velocity = np.sign(self.seek_end_zone_target-self.player.x) * self.player.top_speed
        return (Vector(desired_x_velocity,0.) - self.player.vel)

    def avoid_defenders(self):
        """
        Avoid just the nearest defender by acc directly away from them.
        Ignores anyone not goalward of us, even if they are close and faster than us.
        """
        this=self.player
        ignore_dist=30.
        panic_dist=3.
        #
        nearest=None
        nearest_dist2 = 1e10
        ignore_dist2=ignore_dist**2
        this_end_zone_dist = this.dist_to_attack_end_zone
        for p in self.avoid_defenders_team.players.values():
            if not p.standing: continue
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
            desired_velocity = (this.pos-nearest.pos).norm()*this.top_speed*fac
            desired_acc = desired_velocity - this.vel
            # Don't permit accelerating backwards        
            if (desired_acc.x * this.direction) < 0.:
                desired_acc = Vector(0.,desired_acc.mag()*np.sign(desired_acc.y)) 
            return desired_acc

    def avoid_walls(self):
        this=self.player
        pitch=self.avoid_walls_pitch
        #
        ignore_dist=7.
        panic_dist=2.
        #
        if this.y <= ignore_dist:
            if this.y <= panic_dist:
                desired_acc = Vector(0.,this.top_speed-this.vel.y)*2.
            else:
                fac =  1.-(this.y-panic_dist)/(ignore_dist-panic_dist)
                desired_acc = Vector(0.,(this.top_speed-this.vel.y) * fac)
        elif this.y >= (pitch.ysize-ignore_dist):
            if this.y >= (pitch.ysize-panic_dist):
                desired_acc = Vector(0.,-this.top_speed-this.vel.y)*2.
            else:
                y_diff = pitch.ysize-this.y
                fac = 1.-(y_diff-panic_dist)/(ignore_dist-panic_dist)
                desired_acc = Vector(0.,-(this.top_speed+this.vel.y) * fac)
        else:
            desired_acc = Vector(0,0)
        return desired_acc

    def pursue(self):
        " Go towards projected target position. "
        this=self.player
        # NOTE: Probably better to just assume they are running to EZ than projecting current vel? Or not?
        # NOTE: Maybe this is okay, and covering the EZ is a different behaviour. This one is good for following
        #        a recievers lead to the side.
        # How far to project? Take half distance to target and turn into travel time using their 
        # top speed. Then project their current speed for that time and seek to that position.
        dist = (this.pos-self.pursue_target.pos).mag()/2.
        travel_time = dist/self.pursue_target.top_speed
        projected_pos = self.pursue_target.pos + self.pursue_target.vel * travel_time
        desired_velocity = (projected_pos -this.pos).norm() * this.top_speed
        return desired_velocity - this.vel
        
    def block(self):
        # Magic number, should be set in Team?
        pocket_radius=5.
        this = self.player

        if self.block_target == None:
            # No target, move to in front of the BC
            offset = Vector(pocket_radius*this.direction,0)
            target = self.block_carrier.pos + offset 
        else:
            # Want to move towards their projected position, assuming they will go straight at BC.
            # How far to project? Take half the distance to target player and turn into travel time.
            # Project their velocity for that time and seek to that position.
            dist = (this.pos - self.block_target.pos).mag()/2.
            travel_time = dist/self.block_target.top_speed
            target = self.block_target.pos + self.block_target.vel * travel_time
        
        desired_velocity = (target - this.pos).norm() * this.top_speed
        return (desired_velocity - this.vel)

    def avoid_friends(self):
        """
        Avoids all friends within a certain (small) radius.
        Intended as a means of preventing collisions rather than tactically spreading out.
        """
        this=self.player
        ignore_dist=5.
        #
        acc=Vector(0,0)
        ignore2=ignore_dist**2
        a=1
        for p in self.avoid_friends_team.players.values():
            if this == p: continue
            if not p.standing:continue
            dist2 = (this.pos - p.pos).mag2()
            if dist2 < ignore2:
                acc += (this.pos-p.pos).norm()*this.top_speed*(ignore_dist-np.sqrt(dist2))/ignore_dist*2.
        return acc

    def zone_defend(self):
        """
        Try to keep equidistance between zone limits and other zoners.
        """
        # Magic numbers
        # What fraction of the distance between enemy BC and EZ to aim to sit at?
        # Higher values indicate more aggressive closer defending, lower values more defensive and further back.
        def_factor=0.5
        this = self.owner
        pitch = this.pitch
        vlist=list()
        mlist=list()
        for p in self.zone_defend_team.players.values():
            if p == this: continue
            vnow = this.pos - p.pos
            vlist.append(vnow)
            mlist.append(vnow.mag())
        # Check sides
        if this.y > pitch.ysize/2.:
            vnow = this.y - Vector(0,pitch.ysize)
        else:
            vnow = Vector(0,this.y)*-1
        vlist.append(vnow)
        mlist.append(vnow.mag())
        # Check EZ
        vnow = Vector(this.dist_to_defend_end_zone,0)
        vlist.append(vnow)
        mlist.append(vnow.mag())
        # Forward limit
        bx=pitch.ball.x
        if this.direction > 0:
            b_dist = bx * def_factor*2.
            if this.x > b_dist:
                vnow = Vector(-this.top_speed,0)
            else:
                vnow = Vector(this.x - b_dist,0)
        else:
            b_dist = (pitch.xsize - bx) * def_factor * 2.
            if this.x < (pitch.xsize - b_dist):
                vnow = Vector(this.top_speed,0)
            else:
                vnow = Vector(b_dist - this.x,0)
        vlist.append(vnow)
        mlist.append(vnow.mag())
        # Normalise and combine
        maxd = np.max(mlist)
        mind = np.min(mlist)
        
            
