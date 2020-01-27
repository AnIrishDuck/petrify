import math
import operator

from pint.unit import _Unit

from .. import generic
from ..geometry import AbstractPolygon, Geometry, tau, valid_scalar
from .util import (
    Spatial,
    _connect_point3_line3,
    _connect_point3_sphere,
    _connect_point3_plane,
    _intersect_point3_sphere
)

def operate(op, self, other):
    if valid_scalar(other):
        return self.__class__(op(self.x, other), op(self.y, other), op(self.z, other))

class Vector3(generic.Concrete, generic.Vector, Spatial):
    """
    A three-dimensional vector supporting all corresponding built-in math
    operators:

    >>> Vector(1, 2, 3) + Vector(2, 2, 2)
    Vector(3, 4, 5)
    >>> Vector(1, 2, 3) - Vector(2, 2, 2)
    Vector(-1, 0, 1)
    >>> Vector(1, 0, 1) * 5
    Vector(5, 0, 5)
    >>> Vector(1, 0, 1) / 5
    Vector(0.2, 0.0, 0.2)
    >>> Vector(1, 1, 1) == Vector(1, 1, 1)
    True

    In addition to many other specialized vector operations.

    Defines convenience `.basis` members for commonly used basis vectors:

    >>> Vector.basis.x; Vector.bx
    Vector(1, 0, 0)
    Vector(1, 0, 0)
    >>> Vector.basis.y; Vector.by
    Vector(0, 1, 0)
    Vector(0, 1, 0)
    >>> Vector.basis.z; Vector.bz
    Vector(0, 0, 1)
    Vector(0, 0, 1)

    """
    __slots__ = ['x', 'y', 'z']

    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __copy__(self):
        return self.__class__(self.x, self.y, self.z)

    copy = __copy__

    def __repr__(self):
        return 'Vector({0!r}, {1!r}, {2!r})'.format(*self.xyz)

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def __eq__(self, other):
        if isinstance(other, Vector3):
            return self.__class__ == other.__class__ and \
                   self.x == other.x and \
                   self.y == other.y and \
                   self.z == other.z
        else:
            assert hasattr(other, '__len__') and len(other) == 3
            return self.x == other[0] and \
                   self.y == other[1] and \
                   self.z == other[2]

    def __ne__(self, other):
        return not self.__eq__(other)

    def __nonzero__(self):
        return bool(self.x != 0 or self.y != 0 or self.z != 0)

    def __len__(self):
        return 3

    def __getitem__(self, key):
        return (self.x, self.y, self.z)[key]

    def __setitem__(self, key, value):
        l = [self.x, self.y, self.z]
        l[key] = value
        self.x, self.y, self.z = l

    def __iter__(self):
        return iter((self.x, self.y, self.z))

    def __getattr__(self, name):
        try:
            return tuple([(self.x, self.y, self.z)['xyz'.index(c)] \
                          for c in name])
        except ValueError:
            raise AttributeError(name)

    def __add__(self, other):
        if isinstance(other, Vector3):
            # Vector + Vector -> Vector
            # Vector + Point -> Point
            # Point + Point -> Vector
            if self.__class__ is other.__class__:
                _class = Vector3
            else:
                _class = Point3
            return _class(self.x + other.x,
                          self.y + other.y,
                          self.z + other.z)
        else:
            assert hasattr(other, '__len__') and len(other) == 3
            return self.__class__(self.x + other[0],
                                  self.y + other[1],
                                  self.z + other[2])
    __radd__ = __add__

    def __iadd__(self, other):
        if isinstance(other, Vector3):
            self.x += other.x
            self.y += other.y
            self.z += other.z
        else:
            self.x += other[0]
            self.y += other[1]
            self.z += other[2]
        return self

    def __sub__(self, other):
        if isinstance(other, Vector3):
            # Vector - Vector -> Vector
            # Vector - Point -> Point
            # Point - Point -> Vector
            if self.__class__ is other.__class__:
                _class = Vector3
            else:
                _class = Point3
            return _class(self.x - other.x,
                          self.y - other.y,
                          self.z - other.z)
        else:
            assert hasattr(other, '__len__') and len(other) == 3
            return self.__class__(self.x - other[0],
                                  self.y - other[1],
                                  self.z - other[2])


    def __mul__(self, other):
        if isinstance(other, _Unit):
            assert (1 * other).check('[length]'), 'only compatible with length units'
            return NotImplemented
        elif valid_scalar(other):
            return self.__class__(self.x * other,
                                  self.y * other,
                                  self.z * other)
        else:
            return NotImplemented

    __rmul__ = __mul__

    def __floordiv__(self, other):
        return operate(operator.floordiv, self, other)


    def __rfloordiv__(self, other):
        return operate(operator.floordiv, other, self)

    def __truediv__(self, other):
        return operate(operator.truediv, self, other)

    def __rtruediv__(self, other):
        return operate(operator.truediv, other, self)

    def __neg__(self):
        return self.__class__(-self.x, -self.y, -self.z)

    __pos__ = __copy__

    def __abs__(self):
        return math.sqrt(self.x ** 2 + \
                         self.y ** 2 + \
                         self.z ** 2)

    magnitude = __abs__

    def magnitude_squared(self):
        return self.x ** 2 + \
               self.y ** 2 + \
               self.z ** 2

    def normalize(self):
        d = self.magnitude()
        if d:
            self.x /= d
            self.y /= d
            self.z /= d
        return self

    def normalized(self):
        """
        Returns a vector with the same direction but unit (1) length:

        >>> Vector(0, 0, 5).normalized()
        Vector(0.0, 0.0, 1.0)

        """
        return self / self.magnitude()

    def rounded(self, place=None):
        """
        Rounds all elements to `place` decimals.

        """
        return self.__class__(*(round(v, place) for v in self.xyz))

    def dot(self, other):
        """ The dot product of this vector and the `other`. """
        assert isinstance(other, Vector3)
        return self.x * other.x + \
               self.y * other.y + \
               self.z * other.z

    def cross(self, other):
        """ The cross product of this vector and the `other`. """
        assert isinstance(other, Vector3)
        return Vector3(self.y * other.z - self.z * other.y,
                       -self.x * other.z + self.z * other.x,
                       self.x * other.y - self.y * other.x)

    def reflect(self, normal):
        """
        Reflect this vector across a plane with the given `normal`

        .. note::
            Assumes the given `normal` has unit (1) length.
        """
        assert isinstance(normal, Vector3)
        assert normal.magnitude_squared() == 1
        d = 2 * (self.x * normal.x + self.y * normal.y + self.z * normal.z)
        return self.__class__(self.x - d * normal.x,
                              self.y - d * normal.y,
                              self.z - d * normal.z)

    def rotate(self, axis, theta):
        """
        Return a new vector rotated around `axis` by angle `theta`. Right hand
        rule applies.

        """

        # Adapted from equations published by Glenn Murray.
        # http://inside.mines.edu/~gmurray/ArbitraryAxisRotation/ArbitraryAxisRotation.html
        x, y, z = self.x, self.y,self.z
        u, v, w = axis.x, axis.y, axis.z

        # Extracted common factors for simplicity and efficiency
        r2 = u**2 + v**2 + w**2
        r = math.sqrt(r2)
        ct = math.cos(theta)
        st = math.sin(theta) / r
        dt = (u*x + v*y + w*z) * (1 - ct) / r2
        return Vector3((u * dt + x * ct + (-w * y + v * z) * st),
                       (v * dt + y * ct + ( w * x - u * z) * st),
                       (w * dt + z * ct + (-v * x + u * y) * st))

    def angle(self, other):
        """ Return the angle to the vector other. """
        ratio = self.dot(other) / (self.magnitude()*other.magnitude())
        ratio = max(-1.0, min(1.0, ratio))
        return math.acos(ratio)

    def project(self, other):
        """ Return one vector projected on the vector other. """
        n = other.normalized()
        return self.dot(n)*n

    def snap(self, grid):
        """
        Snaps this vector to a `grid`:

        >>> Vector(1.15, 1.15, 0.9).snap(0.25)
        Vector(1.25, 1.25, 1.0)

        """
        def snap(v):
            return round(v / grid) * grid
        return self.__class__(snap(self.x), snap(self.y), snap(self.z))

    def point(self):
        """ Convert this vector into a point. """
        return Point3(self.x, self.y, self.z)

    class Basis:
        @property
        def x(self): return Vector3(1, 0, 0)

        @property
        def y(self): return Vector3(0, 1, 0)

        @property
        def z(self): return Vector3(0, 0, 1)
    basis = Basis()

generic.Vector.basis = Vector3.basis
Vector = Vector3
Vector3.bx = Vector3.basis.x
Vector3.by = Vector3.basis.y
Vector3.bz = Vector3.basis.z

class Point3(Vector3, generic.Point, Geometry):
    """
    A close cousin of :py:class:`~petrify.space.Vector`, used to represent a
    point instead of a transform:

    >>> Point(1, 2, 3) + Vector(1, 1, 1)
    Point(2, 3, 4)

    Defines a convenience `.origin` attribute for this commonly-used point:

    >>> Point.origin
    Point(0, 0, 0)

    """

    def __repr__(self):
        return 'Point({0!r}, {1!r}, {2!r})'.format(*self.xyz)

    def intersect(self, other):
        """
        Returns whether the point lies within the given `other` sphere:

        """
        return other._intersect_point3(self)

    def _intersect_sphere(self, other):
        return _intersect_point3_sphere(self, other)

    def connect(self, other):
        """
        Find the shortest line segment connecting this object to the `other`
        object.

        """
        return other._connect_point3(self)

    def _connect_point3(self, other):
        if self != other:
            return LineSegment3(other, self)
        return None

    def _connect_line3(self, other):
        c = _connect_point3_line3(self, other)
        if c:
            return c._swap()

    def _connect_sphere(self, other):
        c = _connect_point3_sphere(self, other)
        if c:
            return c._swap()

    def _connect_plane(self, other):
        c = _connect_point3_plane(self, other)
        if c:
            return c._swap()

    def vector(self):
        """ The vector formed from the origin to this point. """
        return Vector3(self.x, self.y, self.z)

Point = Point3
Point3.origin = Point3(0, 0, 0)
generic.Point.origin = Point3.origin
