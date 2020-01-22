from .util import _intersect_line2_line2, _intersect_line2_circle, _connect_circle_line2, _connect_point2_line2

from .planar import Planar
from .point import Point, Point2, Vector, Vector2
from ..geometry import Geometry, tau, valid_scalar

class Line2(Geometry, Planar):
    """
    Represents an infinite line:

    >>> Line(Point(0, 0), Vector(1, 1))
    Line(Point(0, 0), Vector(1, 1))
    >>> Line(Point(0, 0), Point(1, 1))
    Line(Point(0, 0), Vector(1, 1))

    Implements many built-in methods:

    >>> Line(Point(1, 1), Point(2, 1)) + Vector(1, 1)
    Line(Point(2, 2), Vector(1, 0))

    """
    __slots__ = ['p', 'v']

    def __init__(self, *args):
        if len(args) == 3:
            assert isinstance(args[0], Point2) and \
                   isinstance(args[1], Vector2) and \
                   valid_scalar(args[2])
            self.p = args[0].copy()
            self.v = args[1] * args[2] / abs(args[1])
        elif len(args) == 2:
            if isinstance(args[0], Point2) and isinstance(args[1], Point2):
                self.p = args[0].copy()
                self.v = args[1] - args[0]
            elif isinstance(args[0], Point2) and isinstance(args[1], Vector2):
                self.p = args[0].copy()
                self.v = args[1].copy()
            else:
                raise AttributeError('%r' % (args,))
        elif len(args) == 1:
            if isinstance(args[0], Line2):
                self.p = args[0].p.copy()
                self.v = args[0].v.copy()
            else:
                raise AttributeError('%r' % (args,))
        else:
            raise AttributeError('%r' % (args,))

        if not self.v:
            raise AttributeError('Line has zero-length vector')

    def __add__(self, v):
        return self.__class__(self.p + v, self.v)

    def __mul__(self, v):
        return self.__class__(self.p * v, self.v * v)
    __rmul__ = __mul__

    def __neg__(self):
        return self.__class__(self.p2, self.p1)

    def __hash__(self):
        return hash((self.p, self.v))

    def __eq__(self, other):
        return self.p == other.p and self.v == other.v

    def __copy__(self):
        return self.__class__(self.p, self.v)

    copy = __copy__

    def __repr__(self):
        return 'Line({0!r}, {1!r})'.format(self.p, self.v)

    p1 = property(lambda self: self.p)
    p2 = property(lambda self: Point2(self.p.x + self.v.x,
                                      self.p.y + self.v.y))

    def _apply_transform(self, t):
        self.p = t * self.p
        self.v = t * self.v

    def _u_in(self, u):
        return True

    def normalized(self):
        """
        Normalizes this line:

        >>> Line(Point(0, 0), Point(2, 0)).normalized()
        Line(Point(0, 0), Vector(1.0, 0.0))

        """
        return self.__class__(self.p, self.v.normalized())

    def intersect(self, other):
        """
        Finds the intersection of this object and another:

        >>> l = Line(Point(0, 2), Vector(0, -2))
        >>> l.intersect(Line(Point(2, 0), Vector(-2, 0)))
        Point(0.0, 0.0)
        >>> l.intersect(Line(Point(1, 2), Vector(0, -2))) is None
        True
        >>> from petrify.plane import Circle
        >>> l.intersect(Circle(Point(0, 0), 1))
        LineSegment(Point(0.0, -1.0), Point(0.0, 1.0))

        """
        return other._intersect_line2(self)

    def _intersect_line2(self, other):
        return _intersect_line2_line2(self, other)

    def _intersect_circle(self, other):
        return _intersect_line2_circle(self, other)

    def connect(self, other):
        """
        Finds the closest connecting line segment between this object and
        another:

        >>> l = Line(Point(0, 2), Vector(0, -2))
        >>> l.connect(Point(1, 0))
        LineSegment(Point(0.0, 0.0), Point(1.0, 0.0))
        >>> from petrify.plane import Circle
        >>> l.connect(Circle(Point(2, 0), 1))
        LineSegment(Point(0.0, 0.0), Point(1.0, 0.0))

        """
        return other._connect_line2(self)

    def _connect_point2(self, other):
        return _connect_point2_line2(other, self)

    def _connect_line2(self, other):
        return _connect_line2_line2(other, self)

    def _connect_circle(self, other):
        return _connect_circle_line2(other, self)
Line = Line2

class Ray2(Line2):
    """
    Represents a line with an origin point that extends forever:

    >>> Ray(Point(0, 0), Vector(1, 1))
    Ray(Point(0, 0), Vector(1, 1))

    """
    def __repr__(self):
        return 'Ray({0!r}, {1!r})'.format(self.p, self.v)

    def _u_in(self, u):
        return u >= 0.0
Ray = Ray2

class LineSegment2(Line2):
    """
    Represents a line segment:

    >>> LineSegment(Point(0, 0), Vector(1, 1))
    LineSegment(Point(0, 0), Point(1, 1))

    """
    def __repr__(self):
        return 'LineSegment({0!r}, {1!r})'.format(self.p, self.p2)

    def _u_in(self, u):
        return u >= 0.0 and u <= 1.0

    def __abs__(self):
        return abs(self.v)

    def magnitude_squared(self):
        return self.v.magnitude_squared()

    def _swap(self):
        # used by connect methods to switch order of points
        self.p = self.p2
        self.v *= -1
        return self

    length = property(lambda self: abs(self.v))
LineSegment = LineSegment2
