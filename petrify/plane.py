"""
Math utility library for common two-dimensional constructs:

- :py:class:`Vector2`
- :py:class:`Point2`
- :py:class:`Polygon2`
- :py:class:`ComplexPolygon2`
- :py:class:`Matrix2`
- :py:class:`Line2`
- :py:class:`Ray2`
- :py:class:`LineSegment2`

The `pint`_ library can be used to specify dimensions:

>>> from petrify import u
>>> p = Point(24, 12) * u.inches
>>> p.to(u.ft)
<Quantity(Point(2.0, 1.0), 'foot')>

Many methods are nominally supported when wrapped with `pint`. We recommend
you only use units when exporting and importing data, and pick a canonical unit
for all petrify operations.

Big thanks to pyeuclid, the source of most of the code here.

.. note::
    These examples and this library make heavy use of the `tau` constant for
    rotational math *instead* of Pi. Read why at the `Tau Manifesto`_.

.. _`pint`: https://pint.readthedocs.io/en/0.9/
.. _`Tau Manifesto`: https://tauday.com/tau-manifesto

"""
import math
import operator
import types

from . import units
from .geometry import AbstractPolygon, Geometry, tau, valid_scalar
from .solver import solve_matrix

def operate(op, self, other):
    if valid_scalar(other):
        return self.__class__(op(self.x, other), op(self.y, other))

class Planar:
    @property
    def embedding(self):
        from petrify import plane
        return plane

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
    __slots__ = ['x', 'y']

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
        else:
            assert hasattr(other, '__len__') and len(other) == 2
            return self.x == other[0] and \
                   self.y == other[1]

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
        else:
            if not (hasattr(other, '__len__') and len(other) == 2):
                return NotImplemented
            return Vector2(self.x + other[0],
                           self.y + other[1])
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
        else:
            assert hasattr(other, '__len__') and len(other) == 2
            return Vector2(self.x - other[0],
                           self.y - other[1])

    def __rsub__(self, other):
        if isinstance(other, Vector2):
            return Vector2(other.x - self.x,
                           other.y - self.y)
        else:
            assert hasattr(other, '__len__') and len(other) == 2
            return Vector2(other.x - self[0],
                           other.y - self[1])

    def __mul__(self, other):
        if isinstance(other, units.u.Unit):
            assert (1 * other).check('[length]'), 'only compatible with length units'
            return NotImplemented
        elif valid_scalar(other):
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

# a b c  0 3 6
# e f g  1 4 7
# i j k  2 5 8

class Matrix2:
    """
    A matrix that can be used to transform two-dimensional vectors and points.

    """
    __slots__ = list('abcefgijk')

    def __init__(self):
        self.a = 1
        self.b = 0
        self.c = 0
        self.e = 0
        self.f = 1
        self.g = 0
        self.i = 0
        self.j = 0
        self.k = 1

    def __copy__(self):
        M = Matrix2()
        M.a = self.a
        M.b = self.b
        M.c = self.c
        M.e = self.e
        M.f = self.f
        M.g = self.g
        M.i = self.i
        M.j = self.j
        M.k = self.k
        return M

    copy = __copy__
    def __repr__(self):
        return ('Matrix2([% 8.2f % 8.2f % 8.2f\n'  \
                '         % 8.2f % 8.2f % 8.2f\n'  \
                '         % 8.2f % 8.2f % 8.2f])') \
                % (self.a, self.b, self.c,
                   self.e, self.f, self.g,
                   self.i, self.j, self.k)

    def __getitem__(self, key):
        return [self.a, self.e, self.i,
                self.b, self.f, self.j,
                self.c, self.g, self.k][key]

    def __setitem__(self, key, value):
        L = self[:]
        L[key] = value
        (self.a, self.e, self.i,
         self.b, self.f, self.j,
         self.c, self.g, self.k) = L

    def __mul__(self, other):
        if isinstance(other, Matrix2):
            # Caching repeatedly accessed attributes in local variables
            # apparently increases performance by 20%.  Attrib: Will McGugan.
            Aa = self.a
            Ab = self.b
            Ac = self.c
            Ae = self.e
            Af = self.f
            Ag = self.g
            Ai = self.i
            Aj = self.j
            Ak = self.k
            Ba = other.a
            Bb = other.b
            Bc = other.c
            Be = other.e
            Bf = other.f
            Bg = other.g
            Bi = other.i
            Bj = other.j
            Bk = other.k
            C = Matrix2()
            C.a = Aa * Ba + Ab * Be + Ac * Bi
            C.b = Aa * Bb + Ab * Bf + Ac * Bj
            C.c = Aa * Bc + Ab * Bg + Ac * Bk
            C.e = Ae * Ba + Af * Be + Ag * Bi
            C.f = Ae * Bb + Af * Bf + Ag * Bj
            C.g = Ae * Bc + Af * Bg + Ag * Bk
            C.i = Ai * Ba + Aj * Be + Ak * Bi
            C.j = Ai * Bb + Aj * Bf + Ak * Bj
            C.k = Ai * Bc + Aj * Bg + Ak * Bk
            return C
        elif isinstance(other, Point2):
            A = self
            B = other
            P = Point2(0, 0)
            P.x = A.a * B.x + A.b * B.y + A.c
            P.y = A.e * B.x + A.f * B.y + A.g
            return P
        elif isinstance(other, Vector2):
            A = self
            B = other
            V = Vector2(0, 0)
            V.x = A.a * B.x + A.b * B.y
            V.y = A.e * B.x + A.f * B.y
            return V
        else:
            other = other.copy()
            other._apply_transform(self)
            return other
    __rmul__ = __mul__

    def __imul__(self, other):
        assert isinstance(other, Matrix2)
        # Cache attributes in local vars (see Matrix2.__mul__).
        Aa = self.a
        Ab = self.b
        Ac = self.c
        Ae = self.e
        Af = self.f
        Ag = self.g
        Ai = self.i
        Aj = self.j
        Ak = self.k
        Ba = other.a
        Bb = other.b
        Bc = other.c
        Be = other.e
        Bf = other.f
        Bg = other.g
        Bi = other.i
        Bj = other.j
        Bk = other.k
        self.a = Aa * Ba + Ab * Be + Ac * Bi
        self.b = Aa * Bb + Ab * Bf + Ac * Bj
        self.c = Aa * Bc + Ab * Bg + Ac * Bk
        self.e = Ae * Ba + Af * Be + Ag * Bi
        self.f = Ae * Bb + Af * Bf + Ag * Bj
        self.g = Ae * Bc + Af * Bg + Ag * Bk
        self.i = Ai * Ba + Aj * Be + Ak * Bi
        self.j = Ai * Bb + Aj * Bf + Ak * Bj
        self.k = Ai * Bc + Aj * Bg + Ak * Bk
        return self

    # Static constructors
    @classmethod
    def identity(cls):
        self = cls()
        return self

    @classmethod
    def from_values(cls, *values):
        self = cls()
        self[:] = values[:]
        return self

    @classmethod
    def scale(cls, x, y):
        """
        A scale transform:

        >>> Point(1, 1) * Matrix2.scale(2, 3)
        Point(2, 3)

        """
        self = cls()
        self.a = x
        self.f = y
        return self

    @classmethod
    def translate(cls, x, y):
        """
        Translates:

        >>> Point(1, 1) * Matrix2.translate(2, 3)
        Point(3, 4)

        """
        self = cls()
        self.c = x
        self.g = y
        return self

    @classmethod
    def rotate(cls, angle):
        """
        Counter-clockwise rotational transform:

        >>> (Point(1, 0) * Matrix2.rotate(tau / 4)).round(2)
        Point(0.0, 1.0)

        """
        self = cls()
        s = math.sin(angle)
        c = math.cos(angle)
        self.a = self.f = c
        self.b = -s
        self.e = s
        return self

    def determinant(self):
        return (self.a*self.f*self.k
                + self.b*self.g*self.i
                + self.c*self.e*self.j
                - self.a*self.g*self.j
                - self.b*self.e*self.k
                - self.c*self.f*self.i)

    def inverse(self):
        tmp = Matrix2()
        d = self.determinant()

        if abs(d) < 0.001:
            # No inverse, return identity
            return tmp
        else:
            d = 1.0 / d

            tmp.a = d * (self.f*self.k - self.g*self.j)
            tmp.b = d * (self.c*self.j - self.b*self.k)
            tmp.c = d * (self.b*self.g - self.c*self.f)
            tmp.e = d * (self.g*self.i - self.e*self.k)
            tmp.f = d * (self.a*self.k - self.c*self.i)
            tmp.g = d * (self.c*self.e - self.a*self.g)
            tmp.i = d * (self.e*self.j - self.f*self.i)
            tmp.j = d * (self.b*self.i - self.a*self.j)
            tmp.k = d * (self.a*self.f - self.b*self.e)

            return tmp
Matrix = Matrix2


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
        return LineSegment2(other, self)

    def _connect_line2(self, other):
        c = _connect_point2_line2(self, other)
        if c:
            return c._swap()

    def _connect_circle(self, other):
        c = _connect_point2_circle(self, other)
        if c:
            return c._swap()
Point = Point2
Point2.origin = Point2(0, 0)

class Line2(Geometry, Planar):
    """
    Represents an infinite line:

    >>> Line(Point(0, 0), Vector(1, 1))
    Line(Point(0, 0), Vector(1, 1))
    >>> Line(Point(0, 0), Point(1, 1))
    Line(Point(0, 0), Vector(1, 1))

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

class Circle(Geometry):
    __slots__ = ['c', 'r']

    def __init__(self, center, radius):
        assert isinstance(center, Vector2) and valid_scalar(radius)
        self.c = center.copy()
        self.r = radius

    def __copy__(self):
        return self.__class__(self.c, self.r)

    copy = __copy__

    def __repr__(self):
        return 'Circle2({0!r}, {1!r})'.format(self.c, self.r)

    def _apply_transform(self, t):
        self.c = t * self.c

    def intersect(self, other):
        return other._intersect_circle(self)

    def _intersect_point2(self, other):
        return _intersect_point2_circle(other, self)

    def _intersect_line2(self, other):
        return _intersect_line2_circle(other, self)

    def _intersect_circle(self, other):
        return _intersect_circle_circle(other, self)

    def connect(self, other):
        return other._connect_circle(self)

    def _connect_point2(self, other):
        return _connect_point2_circle(other, self)

    def _connect_line2(self, other):
        c = _connect_circle_line2(self, other)
        if c:
            return c._swap()

    def _connect_circle(self, other):
        return _connect_circle_circle(other, self)

    def tangent_points(self, p):
        m = 0.5 * (self.c + p)
        return self.intersect(Circle(m, abs(p - m)))

def _intersect_point2_circle(P, C):
    return abs(P - C.c) <= C.r

def _intersect_line2_line2(A, B):
    d = B.v.y * A.v.x - B.v.x * A.v.y
    if d == 0:
        return None

    dy = A.p.y - B.p.y
    dx = A.p.x - B.p.x
    ua = (B.v.x * dy - B.v.y * dx) / d
    if not A._u_in(ua):
        return None
    ub = (A.v.x * dy - A.v.y * dx) / d
    if not B._u_in(ub):
        return None

    return Point2(A.p.x + ua * A.v.x,
                  A.p.y + ua * A.v.y)

def _intersect_line2_circle(L, C):
    a = L.v.magnitude_squared()
    b = 2 * (L.v.x * (L.p.x - C.c.x) + \
             L.v.y * (L.p.y - C.c.y))
    c = C.c.magnitude_squared() + \
        L.p.magnitude_squared() - \
        2 * C.c.dot(L.p) - \
        C.r ** 2
    det = b ** 2 - 4 * a * c
    if det < 0:
        return None
    sq = math.sqrt(det)
    u1 = (-b + sq) / (2 * a)
    u2 = (-b - sq) / (2 * a)

    if u1 * u2 > 0 and not L._u_in(u1) and not L._u_in(u2):
        return None

    if not L._u_in(u1):
        u1 = max(min(u1, 1.0), 0.0)
    if not L._u_in(u2):
        u2 = max(min(u2, 1.0), 0.0)

    # Tangent
    if u1 == u2:
        return Point2(L.p.x + u1 * L.v.x,
                      L.p.y + u1 * L.v.y)

    return LineSegment2(Point2(L.p.x + u1 * L.v.x,
                               L.p.y + u1 * L.v.y),
                        Point2(L.p.x + u2 * L.v.x,
                               L.p.y + u2 * L.v.y))

def _intersect_circle_circle(A, B):
    d = abs(A.c - B.c)
    s = A.r + B.r
    m = abs(A.r - B.r)
    if d > s or d < m:
        return None
    d2 = d ** 2
    s2 = s ** 2
    m2 = m ** 2
    k = 0.25 * math.sqrt((s2 - d2) * (d2 - m2))
    dr = (A.r ** 2 - B.r ** 2) / d2
    kd = 2 * k / d2
    return (
      Point2(
        0.5 * (A.c.x + B.c.x + (B.c.x - A.c.x) * dr) + (B.c.y - A.c.y) * kd,
        0.5 * (A.c.y + B.c.y + (B.c.y - A.c.y) * dr) - (B.c.x - A.c.x) * kd),
      Point2(
        0.5 * (A.c.x + B.c.x + (B.c.x - A.c.x) * dr) - (B.c.y - A.c.y) * kd,
        0.5 * (A.c.y + B.c.y + (B.c.y - A.c.y) * dr) + (B.c.x - A.c.x) * kd))

def _connect_point2_line2(P, L):
    d = L.v.magnitude_squared()
    assert d != 0
    u = ((P.x - L.p.x) * L.v.x + \
         (P.y - L.p.y) * L.v.y) / d
    if not L._u_in(u):
        u = max(min(u, 1.0), 0.0)
    return LineSegment2(P,
                        Point2(L.p.x + u * L.v.x,
                               L.p.y + u * L.v.y))

def _connect_point2_circle(P, C):
    v = P - C.c
    v = v.normalized()
    v *= C.r
    return LineSegment2(P, Point2(C.c.x + v.x, C.c.y + v.y))

def _connect_line2_line2(A, B):
    d = B.v.y * A.v.x - B.v.x * A.v.y
    if d == 0:
        # Parallel, connect an endpoint with a line
        if isinstance(B, Ray2) or isinstance(B, LineSegment2):
            p1, p2 = _connect_point2_line2(B.p, A)
            return p2, p1
        # No endpoint (or endpoint is on A), possibly choose arbitrary point
        # on line.
        return _connect_point2_line2(A.p, B)

    dy = A.p.y - B.p.y
    dx = A.p.x - B.p.x
    ua = (B.v.x * dy - B.v.y * dx) / d
    if not A._u_in(ua):
        ua = max(min(ua, 1.0), 0.0)
    ub = (A.v.x * dy - A.v.y * dx) / d
    if not B._u_in(ub):
        ub = max(min(ub, 1.0), 0.0)

    return LineSegment2(Point2(A.p.x + ua * A.v.x, A.p.y + ua * A.v.y),
                        Point2(B.p.x + ub * B.v.x, B.p.y + ub * B.v.y))

def _connect_circle_line2(C, L):
    d = L.v.magnitude_squared()
    assert d != 0
    u = ((C.c.x - L.p.x) * L.v.x + (C.c.y - L.p.y) * L.v.y) / d
    if not L._u_in(u):
        u = max(min(u, 1.0), 0.0)
    point = Point2(L.p.x + u * L.v.x, L.p.y + u * L.v.y)
    v = (point - C.c)
    v = v.normalized()
    v *= C.r
    return LineSegment2(Point2(C.c.x + v.x, C.c.y + v.y), point)

def _connect_circle_circle(A, B):
    v = B.c - A.c
    d = v.magnitude()
    if A.r >= B.r and d < A.r:
        #centre B inside A
        s1,s2 = +1, +1
    elif B.r > A.r and d < B.r:
        #centre A inside B
        s1,s2 = -1, -1
    elif d >= A.r and d >= B.r:
        s1,s2 = +1, -1
    v = v.normalized()
    return LineSegment2(Point2(A.c.x + s1 * v.x * A.r, A.c.y + s1 * v.y * A.r),
                        Point2(B.c.x + s2 * v.x * B.r, B.c.y + s2 * v.y * B.r))

class Polygon2(AbstractPolygon, Planar):
    """
    A two-dimensional polygon:

    >>> Polygon([Point(2, 0), Point(0, 0), Point(1, 1)])
    Polygon([Point(2, 0), Point(0, 0), Point(1, 1)])

    Supports scaling and translation:

    >>> tri = Polygon([Point(2, 0), Point(0, 0), Point(1, 1)])
    >>> tri * Vector(2, 3)
    Polygon([Point(4, 0), Point(0, 0), Point(2, 3)])
    >>> tri * Matrix2.scale(2, 3)
    Polygon([Point(4, 0), Point(0, 0), Point(2, 3)])
    >>> tri + Vector(2, 1)
    Polygon([Point(4, 1), Point(2, 1), Point(3, 2)])
    >>> len(tri)
    3

    """
    def __init__(self, points):
        self.points = points

    def __repr__(self):
        return 'Polygon({0!r})'.format(self.points)

    def simplify(self, tolerance=0.0001):
        """
        Remove any duplicate points, within a certain `tolerance`:

        >>> Polygon([Point(1, 1), Point(2, 0), Point(0, 0), Point(1, 1)]).simplify()
        Polygon([Point(2, 0), Point(0, 0), Point(1, 1)])

        Returns `None` if the resulting simplification would create a point:

        >>> Polygon([
        ...     Point(1, 1),
        ...     Point(2, 0),
        ...     Point(0, 0),
        ...     Point(1, 1)
        ... ]).simplify(100) is None
        True

        """
        return super().simplify(tolerance)

    def to_clockwise(self):
        """
        Converts this polygon to a clockwise one if necessary:

        >>> Polygon([Point(2, 0), Point(0, 0), Point(1, 1)]).to_clockwise()
        Polygon([Point(2, 0), Point(0, 0), Point(1, 1)])
        >>> Polygon([Point(1, 1), Point(0, 0), Point(2, 0)]).to_clockwise()
        Polygon([Point(2, 0), Point(0, 0), Point(1, 1)])

        """
        return self if self.clockwise() else self.inverted()

    def to_counterclockwise(self):
        """
        Converts this polygon to a clockwise one if necessary:

        >>> Polygon([Point(2, 0), Point(0, 0), Point(1, 1)]).to_counterclockwise()
        Polygon([Point(1, 1), Point(0, 0), Point(2, 0)])
        >>> Polygon([Point(1, 1), Point(0, 0), Point(2, 0)]).to_counterclockwise()
        Polygon([Point(1, 1), Point(0, 0), Point(2, 0)])

        """
        return self.inverted() if self.clockwise() else self

    def clockwise(self):
        """
        Returns `True` if the points in this polygon are in clockwise order:

        >>> Polygon([Point(2, 0), Point(0, 0), Point(1, 1)]).clockwise()
        True
        >>> Polygon([Point(1, 1), Point(0, 0), Point(2, 0)]).clockwise()
        False

        """
        area = sum((l.p2.x - l.p1.x) * (l.p2.y + l.p1.y) for l in self.segments())
        return area > 0

    def inwards(self, edge):
        """
        Finds the normalized :py:class:`Ray2` facing inwards for a given `edge`:

        >>> tri = Polygon([Point(2, 0), Point(0, 0), Point(1, 1)])
        >>> tri.inwards(tri.segments()[0])
        Vector(0.0, 1.0)

        """
        mid = (edge.p1 + edge.p2) / 2
        ray = Ray2(Point2(*mid), edge.v.cross())

        # NOTE: this still might have issues with parallel lines that intersect
        # the ray drawn from the midpoint along their entire span.
        intersections = (
            (other, ray.intersect(other)) for other in self.segments() if other != edge
        )

        # The intersection can be a point on the outside of the polygon. In this
        # case, it will intersect two segments, even though it has only crossed
        # the boundary of the polygon once. We arbitrarily ignore one of these
        # segments (via the != l.p2 check) to resolve this corner case.
        count = sum(
            1 for l, i in intersections
            if i is not None and i != l.p2
        )
        return (ray if count % 2 == 1 else -ray).v.normalized()

    def offset(self, amount, tolerance=0.0001):
        """
        Finds the dynamic offset of a polygon by moving all edges by a given
        `amount` perpendicular to their direction:

        >>> square = Polygon([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0)])
        >>> square.offset(-0.1)
        Polygon([Point(0.1, 0.1), Point(0.1, 0.9), Point(0.9, 0.9), Point(0.9, 0.1)])
        >>> square.offset(0.1)
        Polygon([Point(-0.1, -0.1), Point(-0.1, 1.1), Point(1.1, 1.1), Point(1.1, -0.1)])
        >>> square.offset(10) is None
        True

        .. note::
            This is currently a naive implementation that does not properly
            handle non-local intersections that can split the polygon.

        """
        def magnitude(line, normal, inwards):
            # u * line.vector + normal = w * inwards
            # w * inwards - u * line.vector = normal
            rows = list(zip(inwards.xy, (-line).xy, normal))
            matrix = list(list(row) for row in rows)
            solution = solve_matrix(matrix)
            return inwards * solution[0]

        amount_squared = amount ** 2
        lines = self.segments()
        inwards = [self.inwards(l) for l in lines]
        remnant = []
        for ai, l, n, bi in zip((inwards[-1], *inwards), lines, inwards, (*inwards[1:], inwards[0])):
            ra = Ray2(l.p1, ai + n)
            rb = Ray2(l.p2, bi + n)

            # We need to find the true magnitude of the "halfway" pair inwards
            # vector. It forms a triangle with the normal and the line itself.
            i = ra.intersect(rb)
            motion = magnitude(l.v, n, ra.v)
            m = motion.magnitude_squared()
            if not i or (i - ra.p).magnitude_squared() / m > amount_squared:
                remnant.append((l, n))

        if not remnant:
            return None

        points = []
        for a, b in zip((remnant[-1], *remnant), remnant):
            al, ai = a
            bl, bi = b

            start = Line2(al.p, al.v).intersect(Line2(bl.p, bl.v))
            motion = magnitude(bl.v, bi, ai + bi)

            points.append(start + (motion * -amount))

        return Polygon(points)


    def inverted(self):
        """
        Reverse the points in this polygon:

        >>> tri = Polygon([Point(2, 0), Point(0, 0), Point(1, 1)])
        >>> tri.inverted()
        Polygon([Point(1, 1), Point(0, 0), Point(2, 0)])

        """
        return Polygon(list(reversed(self.points)))

    def is_convex(self):
        """
        Return True if the polynomial defined by the sequence of 2D
        points is 'strictly convex':

        >>> tri = Polygon([Point(2, 0), Point(0, 0), Point(1, 1)])
        >>> tri.is_convex()
        True
        >>> indent = Polygon([
        ...     Point(0, 0),
        ...     Point(10, 0),
        ...     Point(5, 5),
        ...     Point(10, 10),
        ...     Point(0, 10)
        ... ])
        >>> indent.is_convex()
        False

        .. note::
            "strictly convex" is defined as follows:

            - points are valid
            - side lengths are non-zero
            - interior angles are strictly between zero and a straight angle
            - the polygon does not intersect itself

        """
        # Adapted from https://stackoverflow.com/a/45372025
        # The only change needed was to use our constant for TAU, which again
        # proves its utility
        # NOTES:  1.  Algorithm: the signed changes of the direction angles
        #             from one side to the next side must be all positive or
        #             all negative, and their sum must equal plus-or-minus
        #             one full turn (2 pi radians). Also check for too few,
        #             invalid, or repeated points.
        #         2.  No check is explicitly done for zero internal angles
        #             (180 degree direction-change angle) as this is covered
        #             in other ways, including the `n < 3` check.
        try:  # needed for any bad points or direction changes
            # Check for too few points
            if len(self.points) < 3:
                return False
            # Get starting information
            old_x, old_y = self.points[-2].xy
            new_x, new_y = self.points[-1].xy
            new_direction = math.atan2(new_y - old_y, new_x - old_x)
            angle_sum = 0.0
            # Check each point (the side ending there, its angle) and accum. angles
            for ndx, newpoint in enumerate(self.points):
                # Update point coordinates and side directions, check side length
                old_x, old_y, old_direction = new_x, new_y, new_direction
                new_x, new_y = newpoint.xy
                new_direction = math.atan2(new_y - old_y, new_x - old_x)
                if old_x == new_x and old_y == new_y:
                    return False  # repeated consecutive points
                # Calculate & check the normalized direction-change angle
                angle = new_direction - old_direction
                if angle <= -tau / 2:
                    angle += tau  # make it in half-open interval (-Pi, Pi]
                elif angle > tau / 2:
                    angle -= tau
                if ndx == 0:  # if first time through loop, initialize orientation
                    if angle == 0.0:
                        return False
                    orientation = 1.0 if angle > 0.0 else -1.0
                else:  # if other time through loop, check orientation is stable
                    if orientation * angle <= 0.0:  # not both pos. or both neg.
                        return False
                # Accumulate the direction-change angle
                angle_sum += angle
            # Check that the total number of full turns is plus-or-minus 1
            return abs(round(angle_sum / tau)) == 1
        except (ArithmeticError, TypeError, ValueError):
            return False  # any exception means not a proper convex polygon

    def contains(self, p):
        """
        Tests whether a point lies within this polygon:

        >>> tri = Polygon([Point(2, 0), Point(0, 0), Point(1, 1)])
        >>> tri.contains(Point(1.0, 0.5))
        True
        >>> tri.contains(Point(0.5, 1.5))
        False

        """
        for l in self.segments():
            if l.v.magnitude_squared() > 0 and l.connect(p).v.magnitude_squared() == 0:
                return True
        test = Ray2(Point2(p.x, p.y), Vector2(1, 0))
        intersects = (l.intersect(test) for l in self.segments())
        intersects = set(i for i in intersects if i is not None)
        return len(intersects) % 2 == 1

    def shift(self, n):
        """
        Shift the points in this polygon by `n`:

        >>> tri = Polygon([Point(2, 0), Point(0, 0), Point(1, 1)])
        >>> tri.shift(1)
        Polygon([Point(0, 0), Point(1, 1), Point(2, 0)])

        """
        return Polygon([*self.points[n:], *self.points[:n]])

    def envelope(self):
        """
        Returns the bounding :py:class:`~petrify.shape.Rectangle` around this
        polygon:

        >>> tri = Polygon([Point(2, 0), Point(0, 0), Point(1, 1)])
        >>> tri.envelope()
        Rectangle(Point(0, 0), Vector(2, 1))

        """
        from .shape import Rectangle
        sx = min(p.x for p in self.points)
        sy = min(p.y for p in self.points)
        ex = max(p.x for p in self.points)
        ey = max(p.y for p in self.points)
        return Rectangle(Point2(sx, sy), Vector2(ex-sx, ey-sy))
Polygon = Polygon2

class ComplexPolygon2:
    """
    Represents a complex polygon. A complex polygon is composed of one or more
    separate simple polygons, and may contain holes:

    >>> from petrify.shape import Rectangle
    >>> square = Rectangle(Point(0, 0), Vector(1, 1))
    >>> complex = ComplexPolygon([square + Vector(1, 1), square * 3])
    >>> len(complex)
    8

    """
    def __init__(self, polygons=None, interior=None, exterior=None):
        if polygons is not None:
            self.interior = []
            self.exterior = []
            for ix, polygon in enumerate(polygons):
                simple = polygon.simplify()
                if simple is None:
                    continue

                if not simple.clockwise():
                    simple = simple.inverted()
                first = simple.points[0]
                others = (*polygons[:ix], *polygons[ix + 1:])
                if any(other.contains(first) for other in others):
                    self.interior.append(simple)
                else:
                    self.exterior.append(simple)
        elif interior is not None and exterior is not None:
            self.interior = interior
            self.exterior = exterior

    def to_clockwise(self):
        """
        Converts all sub-polygons to clockwise:

        >>> tri = Polygon([Point(2, 0), Point(0, 0), Point(1, 1)])
        >>> ComplexPolygon([tri]).to_clockwise()
        ComplexPolygon([Polygon([Point(2, 0), Point(0, 0), Point(1, 1)])])
        >>> ComplexPolygon([tri.inverted()]).to_clockwise()
        ComplexPolygon([Polygon([Point(2, 0), Point(0, 0), Point(1, 1)])])

        """
        return ComplexPolygon(
            exterior=[p.to_clockwise() for p in self.exterior],
            interior=[p.to_clockwise() for p in self.interior],
        )

    def to_counterclockwise(self):
        """
        Converts all sub-polygons to counter-clockwise:

        >>> tri = Polygon([Point(2, 0), Point(0, 0), Point(1, 1)])
        >>> ComplexPolygon([tri]).to_counterclockwise()
        ComplexPolygon([Polygon([Point(1, 1), Point(0, 0), Point(2, 0)])])
        >>> ComplexPolygon([tri.inverted()]).to_counterclockwise()
        ComplexPolygon([Polygon([Point(1, 1), Point(0, 0), Point(2, 0)])])

        """
        return ComplexPolygon(
            exterior=[p.to_counterclockwise() for p in self.exterior],
            interior=[p.to_counterclockwise() for p in self.interior],
        )

    def __len__(self):
        return sum(len(p) for p in self.polygons)

    def __repr__(self):
        return "ComplexPolygon({0!r})".format([*self.exterior, *self.interior])

    def segments(self):
        return [s for p in self.polygons for s in p.segments()]

    @property
    def polygons(self):
        return (*self.exterior, *self.interior)

    def offset(self, amount):
        """
        Finds the dynamic offset of this complex polygon by moving all edges by
        a given `amount` perpendicular to their direction.

        Any inner polygons are offset in the reverse direction to the outer
        polygons:

        >>> square = Polygon([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0)])
        >>> complex = ComplexPolygon([square + Vector(1, 1), square * 3])
        >>> complex.offset(-0.1).interior
        [Polygon([Point(0.9, 0.9), Point(0.9, 2.1), Point(2.1, 2.1), Point(2.1, 0.9)])]
        >>> complex.offset(-0.1).exterior
        [Polygon([Point(0.1, 0.1), Point(0.1, 2.9), Point(2.9, 2.9), Point(2.9, 0.1)])]

        """
        from . import engines
        return engines.offset.offset(self, amount)

    def __truediv__(self, v):
        return ComplexPolygon(
            interior=[p / v for p in self.interior],
            exterior=[p / v for p in self.exterior]
        )

    def __mul__(self, v):
        return ComplexPolygon(
            interior=[p * v for p in self.interior],
            exterior=[p * v for p in self.exterior]
        )

    def __add__(self, v):
        return ComplexPolygon(
            interior=[p + v for p in self.interior],
            exterior=[p + v for p in self.exterior]
        )

    def envelope(self):
        """
        Returns the bounding :py:class:`~petrify.shape.Rectangle` around this
        polygon:

        >>> square = Polygon([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0)])
        >>> complex = ComplexPolygon([square + Vector(1, 1), square * 3])
        >>> square.envelope()
        Rectangle(Point(0, 0), Vector(1, 1))

        """
        from .shape import Rectangle
        rectangles = Polygon([p for polygon in self.polygons for p in polygon.envelope().points])
        return rectangles.envelope()
ComplexPolygon = ComplexPolygon2
