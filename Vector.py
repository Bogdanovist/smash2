import scipy as sp
import numpy as np

class Vector(object):
    """
    Utility class to make geometry easier.
    """
    def __init__(self,x,y):
        self.x=x
        self.y=y

    def __add__(self,that):
        return(Vector(self.x+that.x,self.y+that.y))

    def __sub__(self,that):
        return(Vector(self.x-that.x,self.y-that.y))

    def __mul__(self,that):
        """
        If vectors multiplied, silenty assumes you want the dot product.
        """
        if type(that) == Vector:
            return (self.x * that.x + self.y * that.y)
        elif type(float(that)) == float:
            return Vector(self.x * that, self.y * that)

    def norm(self):
        length=self.mag()
        if length < 1e-5:
            return Vector(self.x,self.y)
        else:
            x = self.x/length
            y = self.y/length
            return Vector(x,y)

    def mag(self):
        return np.sqrt((self.x)**2 + (self.y)**2)

    def mag2(self):
        " Magnitude squared to avoid the sqrt "
        return self.x**2 + self.y**2

    def truncate(self,mag):
        """
        Ensures the magnitude of the returned vector is at most as large as the supplied.
        """
        if mag >= self.mag():
            return self
        else:
            return self.norm()*mag