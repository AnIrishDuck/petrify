import math
import operator

from .planar import Planar
from .. import units
from ..geometry import AbstractPolygon, Geometry, tau, valid_scalar

def operate(op, self, other):
    if valid_scalar(other):
        return self.__class__(op(self.x, other), op(self.y, other))
    else:
        return NotImplemented

def partial(v):
    return (isinstance(v, tuple) or isinstance(v, list)) and len(v) == 2

# Fix class in arithmetic methods
# Point + Point should either throw or be a point!
class Vector2(Planar):
    """
    A two-dimensional vector supporting all corresponding built-in math
    operators:

    >>> Vector(1, 2) + Vector(2, 2)
    Vector(3, 4)
    >>> Vector(1, 2) - Vector(2, 2)
    Vector(-1, 0)
    >>> Vector(1, 1) * 5
    Vector(5, 5)
    >>> Vector(1, 1) / 5
    Vector(0.2, 0.2)
    >>> Vector(1, 1) == Vector(1, 1)
    True

    In addition to many other specialized vector operations.

    """
    def __init__(self, x=0, y=0):
        assert valid_scalar(x) and valid_scalar(y)
        self.x = x
        self.y = y

    def __copy__(self):
        return self.__class__(self.x, self.y)

    copy = __copy__

    def __repr__(self):
        return 'Vector({0!r}, {1!r})'.format(self.x, self.y)

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        if isinstance(other, Vector2):
            return self.x == other.x and \
                   self.y == other.y
        elif partial(other):
            return self.x == other[0] and \
                   self.y == other[1]
        else:
            return NotImplemented

    def __ne__(self, other):
        return not self.__eq__(other)

    def __nonzero__(self):
        return bool(self.x != 0 or self.y != 0)

    def __len__(self):
        return 2

    def __getitem__(self, key):
        return (self.x, self.y)[key]

    def __setitem__(self, key, value):
        l = [self.x, self.y]
        l[key] = value
        self.x, self.y = l

    def __iter__(self):
        return iter((self.x, self.y))

    def __getattr__(self, name):
        try:
            return tuple([(self.x, self.y)['xy'.index(c)] \
                          for c in name])
        except ValueError:
            raise AttributeError(name)

    def __add__(self, other):
        if isinstance(other, Vector2):
            # Vector + Vector -> Vector
            # Vector + Point -> Point
            # Point + Point -> Vector
            if self.__class__ is other.__class__:
                _class = Vector2
            else:
                _class = Point2
            return _class(self.x + other.x,
                          self.y + other.y)
        elif partial(other):
            return Vector2(self.x + other[0],
                           self.y + other[1])
        else:
            return NotImplemented
    __radd__ = __add__

    def __iadd__(self, other):
        if isinstance(other, Vector2):
            self.x += other.x
            self.y += other.y
        else:
            self.x += other[0]
            self.y += other[1]
        return self

    def __sub__(self, other):
        if isinstance(other, Vector2):
            # Vector - Vector -> Vector
            # Vector - Point -> Point
            # Point - Point -> Vector
            if self.__class__ is other.__class__:
                _class = Vector2
            else:
                _class = Point2
            return _class(self.x - other.x,
                          self.y - other.y)
        elif partial(other):
            return Vector2(self.x - other[0],
                           self.y - other[1])
        else:
            return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, Vector2):
            return Vector2(other.x - self.x,
                           other.y - self.y)
        elif partial(other):
            return Vector2(other.x - self[0],
                           other.y - self[1])
        else:
            return NotImplemented

    def __mul__(self, other):
        if valid_scalar(other):
            return self.__class__(self.x * other, self.y * other)
        else:
            return NotImplemented

    __rmul__ = __mul__

    def __div__(self, other):
        return operate(operator.div, self, other)

    def __rdiv__(self, other):
        return operate(operator.div, self, other)

    def __floordiv__(self, other):
        return operate(operator.floordiv, self, other)

    def __rfloordiv__(self, other):
        return operate(operator.floordiv, self, other)

    def __truediv__(self, other):
        return operate(operator.truediv, self, other)

    def __rtruediv__(self, other):
        return operate(operator.truediv, self, other)

    def __neg__(self):
        return self.__class__(-self.x, -self.y)

    __pos__ = __copy__

    def __abs__(self):
        return math.sqrt(self.x ** 2 + \
                         self.y ** 2)

    magnitude = __abs__

    def magnitude_squared(self):
        return self.x ** 2 + \
               self.y ** 2

    def normalized(self):
        """
        Return a new vector normalized to unit length:

        >>> Vector(0, 5).normalized()
        Vector(0.0, 1.0)

        """
        d = self.magnitude()
        if d:
            return self.__class__(self.x / d, self.y / d)
        return self.copy()

    def dot(self, other):
        """
        The dot product of this vector and `other`:

        >>> Vector(2, 1).dot(Vector(2, 3))
        7
        """
        assert isinstance(other, Vector2)
        return self.x * other.x + \
               self.y * other.y

    def cross(self):
        return self.__class__(self.y, -self.x)

    def reflected(self, normal):
        """
        Reflects this vector across a line with the given perpendicular
        `normal`:

        >>> Vector(1, 1).reflected(Vector(0, 1))
        Vector(1, -1)

        .. warning::
            Assumes `normal` is normalized (has unit length).
        """
        # assume normal is normalized
        assert isinstance(normal, Vector2)
        d = 2 * (self.x * normal.x + self.y * normal.y)
        return self.__class__(self.x - d * normal.x,
                              self.y - d * normal.y)

    def angle(self, other):
        """
        Return the angle to the vector other:

        >>> Vector(1, 0).angle(Vector(0, 1)) == tau / 4
        True

        """
        ratio = self.dot(other) / (self.magnitude()*other.magnitude())
        ratio = max(-1.0, min(1.0, ratio))
        return math.acos(ratio)

    def project(self, other):
        """ Return one vector projected on the vector other """
        n = other.normalized()
        return self.dot(n)*n

    def round(self, places):
        """
        Rounds this vector to the given decimal place:

        >>> Vector(1.00001, 1.00001).round(2)
        Vector(1.0, 1.0)
        """
        return self.__class__(round(self.x, places), round(self.y, places))

    def snap(self, grid):
        """
        Snaps this vector to a `grid`:

        >>> Vector(1.15, 1.15).snap(0.25)
        Vector(1.25, 1.25)
        """
        def snap(v):
            return round(v / grid) * grid
        return self.__class__(snap(self.x), snap(self.y))
Vector = Vector2

class Point2(Vector2, Geometry):
    """
    A close cousin of :py:class:`Vector2` used to represent points:

    >>> Point(1, 1) + Vector(2, 3)
    Point(3, 4)
    >>> Point(1, 2) * 2
    Point(2, 4)

    """
    def __repr__(self):
        return 'Point({0!r}, {1!r})'.format(self.x, self.y)

    def intersect(self, other):
        """
        Used to determine if this point is within a circle:

        >>> Point(1, 1).intersect(Circle(Point(0, 0), 2))
        True
        >>> Point(3, 3).intersect(Circle(Point(0, 0), 2))
        False

        """
        return other._intersect_point2(self)

    def _intersect_circle(self, other):
        return _intersect_point2_circle(self, other)

    def connect(self, other):
        """
        Connects this point to the other given geometry:

        >>> Point(1, 1).connect(Line(Point(0, 0), Vector(1, 0)))
        LineSegment(Point(1, 1), Point(1.0, 0.0))
        >>> Point(1, 1).connect(Point(0, 0))
        LineSegment(Point(1, 1), Point(0, 0))
        >>> Point(0, 2).connect(Circle(Point(0, 0), 1))
        LineSegment(Point(0, 2), Point(0.0, 1.0))

        """
        return other._connect_point2(self)

    def _connect_point2(self, other):
        from . import LineSgment2
        return LineSegment2(other, self)

    def _connect_line2(self, other):
        from .util import _connect_point2_line2
        c = _connect_point2_line2(self, other)
        if c:
            return c._swap()

    def _connect_circle(self, other):
        from .util import _connect_point2_circle
        c = _connect_point2_circle(self, other)
        if c:
            return c._swap()
Point = Point2
Point2.origin = Point2(0, 0)
