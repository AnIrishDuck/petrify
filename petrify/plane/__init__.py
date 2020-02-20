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
import types

from .util import (
    _intersect_point2_circle,
    _intersect_line2_line2,
    _intersect_line2_circle,
    _connect_circle_line2,
    _connect_point2_circle,
    _connect_point2_line2
)

from .planar import Planar
from .point import Point, Point2, Vector, Vector2
from .line import Line, Line2, LineSegment, LineSegment2, Ray, Ray2

from ..geometry import AbstractPolygon, Geometry, tau, valid_scalar
from ..solver import solve_matrix

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
    >>> tri - Vector(1, 1)
    Polygon([Point(1, -1), Point(-1, -1), Point(0, 0)])
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

    def centered(self, point):
        """
        Center this polygon at a given point:

        >>> from petrify.shape import Rectangle
        >>> Rectangle(Point(0, 0), Vector(2, 2)).centered(Point(3, 3))
        Polygon([Point(2.0, 2.0), Point(2.0, 4.0), Point(4.0, 4.0), Point(4.0, 2.0)])

        """
        return super().centered(point)

    def offset(self, amount):
        """
        Finds the dynamic offset of a polygon by moving all edges by a given
        `amount` perpendicular to their direction:

        >>> square = Polygon([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0)])
        >>> square.offset(-0.1).exterior[0]
        Polygon([Point(0.1, 0.1), Point(0.1, 0.9), Point(0.9, 0.9), Point(0.9, 0.1)])
        >>> square.offset(0.1).exterior[0]
        Polygon([Point(-0.1, -0.1), Point(-0.1, 1.1), Point(1.1, 1.1), Point(1.1, -0.1)])
        >>> square.offset(-10)
        ComplexPolygon([])

        .. note::
            This always returns a :py:class:`ComplexPolygon`. Collisions during
            the offset process can subdivide the polygon.

        """
        return ComplexPolygon(exterior=[self], interior=[]).offset(amount)

    def index_of(self, point):
        """
        Finds index of given `point`:

        >>> Polygon([Point(0, 0), Point(1, 0), Point(1, 1)]).index_of(Point(1, 1))
        2

        """
        return super().index_of(point)

    def inverted(self):
        """
        Reverse the points in this polygon:

        >>> tri = Polygon([Point(2, 0), Point(0, 0), Point(1, 1)])
        >>> tri.inverted()
        Polygon([Point(1, 1), Point(0, 0), Point(2, 0)])

        """
        return super().inverted()

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
        from ..shape import Rectangle
        sx = min(p.x for p in self.points)
        sy = min(p.y for p in self.points)
        ex = max(p.x for p in self.points)
        ey = max(p.y for p in self.points)
        return Rectangle(Point2(sx, sy), Vector2(ex-sx, ey-sy))
Polygon2.PointsConstructor = Polygon2
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

    Supports common built-in methods:

    >>> square = Rectangle(Point(0, 0), Vector(1, 1))
    >>> ComplexPolygon([square]) + Vector(1, 1)
    ComplexPolygon([Polygon([Point(1, 1), Point(1, 2), Point(2, 2), Point(2, 1)])])
    >>> ComplexPolygon([square]) - Vector(1, 1)
    ComplexPolygon([Polygon([Point(-1, -1), Point(-1, 0), Point(0, 0), Point(0, -1)])])

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

    @property
    def points(self):
        return (p for polygon in self.polygons for p in polygon.points)

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
        from .. import engines
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

    def __sub__(self, v):
        return self + (-v)

    def envelope(self):
        """
        Returns the bounding :py:class:`~petrify.shape.Rectangle` around this
        polygon:

        >>> square = Polygon([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0)])
        >>> complex = ComplexPolygon([square + Vector(1, 1), square * 3])
        >>> complex.envelope()
        Rectangle(Point(0, 0), Vector(3, 3))

        """
        from ..shape import Rectangle
        rectangles = Polygon([p for polygon in self.polygons for p in polygon.envelope().points])
        return rectangles.envelope()

    def centered(self, point):
        """
        Center this polygon at a given point:

        >>> from petrify.shape import Rectangle
        >>> ComplexPolygon([
        ...   Rectangle(Point(0, 0), Vector(2, 2)),
        ...   Rectangle(Point(1, 1), Vector(1, 1)),
        ... ]).centered(Point(3, 3)).envelope()
        Rectangle(Point(2.0, 2.0), Vector(2.0, 2.0))

        """
        from ..util import center
        return center(self, point)
ComplexPolygon = ComplexPolygon2
