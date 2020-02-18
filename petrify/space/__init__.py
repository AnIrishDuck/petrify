"""
Math utility library for common three-dimensional constructs:

- :py:class:`Vector3`
- :py:class:`Point3`
- :py:class:`Polygon3`
- :py:class:`Matrix3`
- :py:class:`Line3`
- :py:class:`Ray3`
- :py:class:`LineSegment3`
- :py:class:`Plane`
- :py:class:`PlanarPolygon`
- :py:class:`Face`
- :py:class:`Quaternion`

The `pint`_ library can be used to specify dimensions:

>>> from petrify import u
>>> p = Point(50, 25, 50) * u.mm
>>> p.to('m')
<Quantity(Point(0.05, 0.025, 0.05), 'meter')>

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

from pint.unit import _Unit

from .point import Point, Point3, Vector, Vector3
from .transform import Matrix, Matrix3, Quaternion

from .. import decompose, generic, plane, visualize
from ..plane import Point2, Polygon2, Vector2
from ..geometry import AbstractPolygon, Geometry, tau, valid_scalar

from .util import (
    Spatial,
    _connect_point3_line3,
    _connect_point3_sphere,
    _connect_point3_plane,
    _connect_line3_line3,
    _connect_line3_plane,
    _connect_sphere_line3,
    _connect_sphere_sphere,
    _connect_sphere_plane,
    _connect_plane_plane,
    _intersect_point3_sphere,
    _intersect_line3_sphere,
    _intersect_line3_plane,
    _intersect_plane_plane,
    _pmap
)

class Polygon3(AbstractPolygon, Spatial):
    """
    A linear cycle of coplanar convex points:

    >>> tri= Polygon([Point(0, 0, 0), Point(0, 2, 0), Point(1, 1, 0)])
    >>> tri.plane
    Plane(Vector(0.0, 0.0, -1.0), 0.0)
    >>> tri * Vector(1, 2, 3)
    Polygon([Point(0, 0, 0), Point(0, 4, 0), Point(1, 2, 0)])
    >>> tri * Matrix3.scale(1, 2, 3)
    Polygon([Point(0, 0, 0), Point(0, 4, 0), Point(1, 2, 0)])
    >>> tri + Vector(1, 2, 1)
    Polygon([Point(1.0, 2.0, 1.0), Point(1.0, 4.0, 1.0), Point(2.0, 3.0, 1.0)])
    >>> len(tri)
    3

    """

    def __init__(self, points):
        self.points = points
        self.plane = Plane(*points[0:3])

    def inverted(self):
        """
        Reverses the points on a given polygon:

        >>> p = Polygon([Point(0, 0, 0), Point(1, 0, 0), Point(1, 1, 0)])
        >>> p.inverted()
        Polygon([Point(1, 1, 0), Point(1, 0, 0), Point(0, 0, 0)])

        """
        return super().inverted()

    def index_of(self, point):
        """
        Finds index of given `point`:

        >>> p = Polygon([Point(0, 0, 0), Point(1, 0, 0), Point(1, 1, 0)])
        >>> p.index_of(Point(1, 1))
        2

        """
        return super().index_of(point)

    def segments(self):
        """ Returns all line segments composing this polygon's edges. """
        paired = zip(self.points, self.points[1:] + [self.points[0]])
        return [LineSegment3(a, b) for a, b in paired]

    def simplify(self, tolerance = 0.0001):
        """
        Remove any duplicate points, within a certain `tolerance`:

        >>> Polygon([Point(1, 1, 0), Point(2, 0, 0), Point(0, 0, 0), Point(1, 1, 0)]).simplify()
        Polygon([Point(2, 0, 0), Point(0, 0, 0), Point(1, 1, 0)])

        Returns `None` if the resulting simplification would create a point:

        >>> Polygon([Point(1, 1, 0), Point(2, 0, 0), Point(0, 0, 0)]).simplify(100) is None
        True

        """
        return super().simplify(tolerance)

    def has_edge(self, edge):
        """ Returns true if this polygon contains the given `edge`. """
        return any(l == edge for l in self.segments())

    def mesh(self):
        return visualize.segments(
            ((l, [0, 1, 0]) for l in self.segments())
        )

    def render(self):
        """
        Visualize this polygon in a Jupyter notebook.

        """
        return visualize.scene([self])

    def __repr__(self):
        return "Polygon({0!r})".format(self.points)

    def __len__(self):
        return len(self.points)
Polygon3.PointsConstructor = Polygon3
Polygon = Polygon3

class Line3(Spatial):
    """
    An infinite line:

    >>> Line(Point(0, 0, 0), Vector(1, 1, 1))
    Line(Point(0, 0, 0), Vector(1, 1, 1))
    >>> Line(Point(0, 0, 0), Point(1, 1, 1))
    Line(Point(0, 0, 0), Vector(1, 1, 1))

    """
    __slots__ = ['p', 'v']

    def __init__(self, *args):
        if len(args) == 3:
            assert isinstance(args[0], Point3) and \
                   isinstance(args[1], Vector3) and \
                   valid_scalar(args[2])
            self.p = args[0].copy()
            self.v = args[1] * args[2] / abs(args[1])
        elif len(args) == 2:
            if isinstance(args[0], Point3) and isinstance(args[1], Point3):
                self.p = args[0].copy()
                self.v = args[1] - args[0]
            elif isinstance(args[0], Point3) and isinstance(args[1], Vector3):
                self.p = args[0].copy()
                self.v = args[1].copy()
            else:
                raise AttributeError('%r' % (args,))
        elif len(args) == 1:
            if isinstance(args[0], Line3):
                self.p = args[0].p.copy()
                self.v = args[0].v.copy()
            else:
                raise AttributeError('%r' % (args,))
        else:
            raise AttributeError('%r' % (args,))

        # XXX This is annoying.
        #if not self.v:
        #    raise AttributeError('Line has zero-length vector')

    def __hash__(self):
        return hash((self.p, self.v))

    def __eq__(self, other):
        return (self.p, self.v) == (self.p, self.v)

    def __copy__(self):
        return self.__class__(self.p, self.v)

    copy = __copy__

    def __repr__(self):
        return 'Line({0!r}, {1!r})'.format(self.p, self.v)

    p1 = property(lambda self: self.p)
    p2 = property(lambda self: Point3(self.p.x + self.v.x,
                                      self.p.y + self.v.y,
                                      self.p.z + self.v.z))

    def _apply_transform(self, t):
        self.p = t * self.p
        self.v = t * self.v

    def _u_in(self, u):
        return True

    def intersect(self, other):
        """
        Find the point where this line intersects the `other` plane or sphere:

        >>> l = Line(Point(0, 0, 0), Vector(1, 1, 1));
        >>> p = Plane(Vector(0, 0, 1), 2);
        >>> l.intersect(p)
        Point(2.0, 2.0, 2.0)

        """
        return other._intersect_line3(self)

    def _intersect_sphere(self, other):
        return _intersect_line3_sphere(self, other)

    def _intersect_plane(self, other):
        return _intersect_line3_plane(self, other)

    def connect(self, other):
        """
        Find the shortest line segment connecting this object to the `other`
        object.

        """
        return other._connect_line3(self)

    def _connect_point3(self, other):
        return _connect_point3_line3(other, self)

    def _connect_line3(self, other):
        return _connect_line3_line3(other, self)

    def _connect_sphere(self, other):
        return _connect_sphere_line3(other, self)

    def _connect_plane(self, other):
        c = _connect_line3_plane(self, other)
        if c:
            return c
Line = Line3

class Ray3(Line3):
    """
    A :py:class:`Line` with a fixed origin that continues indefinitely in the given
    direction.

    """
    def __repr__(self):
        return 'Ray({0!r}, {1!r})'.format(self.p, self.v)

    def _u_in(self, u):
        return u >= 0.0
Ray = Ray3

class LineSegment3(Line3):
    def __hash__(self):
        return hash((self.p, self.v))

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

    def __eq__(self, other):
        if isinstance(other, LineSegment3):
            return (
                (self.p1 == other.p1 and self.p2 == other.p2) or
                (self.p2 == other.p1 and self.p1 == other.p2)
            )
        raise RuntimeError("Cannot compute on: " + repr(other))

    @property
    def points(self):
        return [self.p1, self.p2]

    def mesh(self):
        return visualize.segments([(self, [0, 1, 0])])

    def flipped(self):
        return LineSegment3(self.p2, -self.v)

    def endpoints(self):
        return [self.p1, self.p2]

    def has_endpoint(self, p):
        return self.p1 == p or self.p2 == p

    def touches(self, other):
        if isinstance(other, Point3):
            return self.has_endpoint(other)
        if isinstance(other, LineSegment3):
            return self.has_endpoint(other.p1) or self.has_endpoint(other.p2)
        raise RuntimeError("Cannot compute on: " + repr(other))

    length = property(lambda self: abs(self.v))
LineSegment = LineSegment3

class Sphere:
    """
    A perfect sphere with the provided `center` and `radius`:

    >>> Sphere(Point(0, 0, 0), 1.0)
    Sphere(Point(0, 0, 0), 1.0)

    """
    __slots__ = ['c', 'r']

    def __init__(self, center, radius):
        assert isinstance(center, Point3) and valid_scalar(radius)
        self.c = center.copy()
        self.r = radius

    def __copy__(self):
        return self.__class__(self.c, self.r)

    copy = __copy__

    def __repr__(self):
        return 'Sphere({0!r}, {1})'.format(self.c, self.r)

    def _apply_transform(self, t):
        self.c = t * self.c

    def intersect(self, other):
        """
        Checks whether the `other` point lies within this sphere.

        """
        return other._intersect_sphere(self)

    def _intersect_point3(self, other):
        return _intersect_point3_sphere(other, self)

    def _intersect_line3(self, other):
        return _intersect_line3_sphere(other, self)

    def connect(self, other):
        """
        Find the shortest line segment connecting this object to the `other`
        object.

        """
        return other._connect_sphere(self)

    def _connect_point3(self, other):
        return _connect_point3_sphere(other, self)

    def _connect_line3(self, other):
        c = _connect_sphere_line3(self, other)
        if c:
            return c._swap()

    def _connect_sphere(self, other):
        return _connect_sphere_sphere(other, self)

    def _connect_plane(self, other):
        c = _connect_sphere_plane(self, other)
        if c:
            return c

class Plane:
    """
    A three-dimensional plane.

    Can be constructed with three coplanar points:

    >>> Plane(Point(0, 0, 0), Point(1, 0, 0), Point(0, 1, 0))
    Plane(Vector(0.0, 0.0, 1.0), 0.0)

    Or an origin point and two basis vectors:
    >>> Plane(Point(0, 0, 0), Vector.basis.x, Vector.basis.y)
    Plane(Vector(0.0, 0.0, 1.0), 0.0)

    Or a normal and solution scalar / point:

    >>> Plane(Vector.basis.z, 0)
    Plane(Vector(0.0, 0.0, 1.0), 0)
    >>> Plane(Vector.basis.z, Point.origin)
    Plane(Vector(0.0, 0.0, 1.0), 0.0)

    `Plane` also defines convenience methods for commonly used origin planes:

    >>> Plane.xy
    Plane(Vector(0.0, 0.0, 1.0), 0.0)
    >>> Plane.xz
    Plane(Vector(0.0, 1.0, 0.0), 0.0)
    >>> Plane.yz
    Plane(Vector(1.0, 0.0, 0.0), 0.0)

    """
    # n.p = k, where n is normal, p is point on plane, k is constant scalar
    __slots__ = ['n', 'k']

    def __init__(self, *args):
        if len(args) == 3:
            if isinstance(args[0], Point3):
                if all(isinstance(a, Point3) for a in args[1:]):
                    self.n = (args[1] - args[0]).cross(args[2] - args[0])
                    self.n.normalize()
                elif all(isinstance(a, Vector3) for a in args[1:]):
                    self.n = args[1].cross(args[2])
                    self.n.normalize()
                else:
                    raise TypeError('Cannot instantiate Vector from {0!r}'.format(args))
                self.k = self.n.dot(args[0])
        elif len(args) == 2:
            if not isinstance(args[0], Vector3):
                raise TypeError('Cannot instantiate Vector from {0!r}'.format(args))
            self.n = args[0].normalized()
            if isinstance(args[0], Vector3) and isinstance(args[1], Point3):
                self.k = self.n.dot(args[1])
            elif isinstance(args[0], Vector3) and valid_scalar(args[1]):
                self.k = args[1]
            else:
                raise TypeError('Cannot instantiate Vector from {0!r}'.format(args))

        else:
            raise TypeError('Cannot instantiate Vector from {0!r}'.format(args))

        if not self.n:
            raise AttributeError('Points are collinear and do not form plane')

    def __copy__(self):
        return self.__class__(self.n, self.k)

    copy = __copy__

    def __repr__(self):
        return 'Plane({0!r}, {1!r})'.format(self.n, self.k)

    def _get_point(self):
        # Return an arbitrary point on the plane
        if self.n.z:
            return Point3(0., 0., self.k / self.n.z)
        elif self.n.y:
            return Point3(0., self.k / self.n.y, 0.)
        else:
            return Point3(self.k / self.n.x, 0., 0.)

    def _apply_transform(self, t):
        p = t * self._get_point()
        self.n = t * self.n
        self.k = self.n.dot(p)

    def intersect(self, other):
        """
        Find the point where this plane intersects the `other` line or plane:

        >>> Plane(Vector(0, 1, 0), 1).intersect(Plane(Vector(1, 0, 0), 2))
        Line(Point(2.0, 1.0, 0.0), Vector(0.0, 0.0, 1.0))
        >>> Plane(Vector(0, 0, 1), 2).intersect(Line(Point(0, 0, 0), Vector(1, 1, 1)))
        Point(2.0, 2.0, 2.0)

        """
        return other._intersect_plane(self)

    def _intersect_line3(self, other):
        return _intersect_line3_plane(other, self)

    def _intersect_plane(self, other):
        return _intersect_plane_plane(self, other)

    def connect(self, other):
        """
        Find the shortest line segment connecting this object to the `other`
        object.

        """
        return other._connect_plane(self)

    def _connect_point3(self, other):
        return _connect_point3_plane(other, self)

    def _connect_line3(self, other):
        return _connect_line3_plane(other, self)

    def _connect_sphere(self, other):
        return _connect_sphere_plane(other, self)

    def _connect_plane(self, other):
        return _connect_plane_plane(other, self)

    @property
    def normal(self): return self.n

Plane.xy = Plane(Vector3(0.0, 0.0, 1.0), 0.0)
Plane.xz = Plane(Vector3(0.0, 1.0, 0.0), 0.0)
Plane.yz = Plane(Vector3(1.0, 0.0, 0.0), 0.0)

class Basis:
    """
    Embeds a two-dimensional space into a three-dimensional space:

    >>> basis = Basis(Point(1, 0, 0), Vector.basis.y, Vector.basis.z)
    >>> basis.project(Point2(2, 3))
    Point(1, 2, 3)
    >>> basis.project(Vector2(-2, -3))
    Vector(1, -2, -3)

    Can be translated:

    >>> translated = basis.xy + Vector(0, 0, 2)
    >>> translated
    Basis(Point(0, 0, 2), Vector(1, 0, 0), Vector(0, 1, 0))
    >>> translated.project(Point2(2, 3))
    Point(2, 3, 2)

    .. note ::
        Any given :class:`Plane` has an infinite number of associated
        :class:`Basis` constructions.

    There are special `Basis` objects for commonly used bases:

    >>> Basis.unit
    Basis(Point(0, 0, 0), Vector(1, 0, 0), Vector(0, 1, 0))
    >>> Basis.xy
    Basis(Point(0, 0, 0), Vector(1, 0, 0), Vector(0, 1, 0))
    >>> Basis.yz
    Basis(Point(0, 0, 0), Vector(0, 1, 0), Vector(0, 0, 1))
    >>> Basis.xz
    Basis(Point(0, 0, 0), Vector(1, 0, 0), Vector(0, 0, 1))

    """
    def __init__(self, origin, bx, by):
        assert isinstance(origin, Point3)
        assert isinstance(bx, Vector3)
        assert isinstance(by, Vector3)
        assert bx.angle(by) > 0
        self.origin = origin
        self.bx = bx
        self.by = by

    def __add__(self, v):
        if not isinstance(v, Vector3): return NotImplemented
        return Basis(self.origin + v, self.bx, self.by)

    def __repr__(self):
        return "Basis({0.origin!r}, {0.bx!r}, {0.by!r})".format(self)

    def project(self, v):
        p = self.origin + self.bx * v.x + self.by * v.y
        if isinstance(v, plane.Point):
            return p
        elif isinstance(v, plane.Vector):
            return p.vector()
        else:
            return NotImplemented

    def normal(self):
        return self.bx.cross(self.by)

    def grid(self, ticks, count):
        """
        Returns a visual :py:class:`petrify.visualize.Grid` of the projected
        space.

        """
        from .visualize import Grid
        return Grid(self, ticks, count)

Basis.unit = Basis(Point.origin, Vector.basis.x, Vector.basis.y)
Basis.xy = Basis.unit
Basis.yz = Basis(Point.origin, Vector.basis.y, Vector.basis.z)
Basis.xz = Basis(Point.origin, Vector.basis.x, Vector.basis.z)

class PlanarPolygon:
    """
    A two-dimensional :class:`~petrify.plane.Polygon2` or
    :class:`~petrify.plane.ComplexPolygon2` embedded in three-dimensional space
    via a :class:`Basis`:

    >>> tri = plane.Polygon2([
    ...     plane.Point2(0, 0),
    ...     plane.Point2(0, 2),
    ...     plane.Point2(1, 1)
    ... ])
    >>> triangle = PlanarPolygon(Basis.xy, tri)
    >>> triangle.project()
    [Polygon([Point(0, 0, 0), Point(0, 2, 0), Point(1, 1, 0)])]

    """

    def __init__(self, basis, polygon):
        self.basis = basis
        self.polygon = polygon

    @property
    def points(self):
        return [p for exterior in [True, False]
                for polygon in self.project(exterior)
                for p in polygon.points]

    def project(self, exterior=True):
        def simple(polygon):
            return Polygon3([self.basis.project(p) for p in polygon.points])

        if isinstance(self.polygon, plane.Polygon):
            return [simple(self.polygon)] if exterior else []
        elif isinstance(self.polygon, plane.ComplexPolygon):
            polygons = self.polygon.exterior if exterior else self.polygon.interior
            return [simple(p) for p in  polygons]
        else:
            return NotImplemented

    def to_face(self, direction):
        return Face(self.basis, direction, self.polygon)

    def mesh(self, colors={}):
        import pythreejs as js
        import numpy as np

        lines = []
        line_colors = []

        red = [1, 0, 0]
        green = [0, 1, 0]
        exterior = self.project(exterior=True)
        interior = self.project(exterior=False)
        for color, polygons in zip([green, red], [exterior, interior]):
            for polygon in polygons:
                for segment in polygon.segments():
                    lines.extend([segment.p1, segment.p2])
                    line_colors.extend([color, color])

        lines = np.array(lines, dtype=np.float32)
        line_colors = np.array(line_colors, dtype=np.float32)
        geometry = js.BufferGeometry(
            attributes={
                'position': js.BufferAttribute(lines, normalized=False),
                'color': js.BufferAttribute(line_colors, normalized=False),
            },
        )
        material = js.LineBasicMaterial(vertexColors='VertexColors', linewidth=1)
        return js.LineSegments(geometry, material)

    def render(self):
        """
        Visualize this polygon in a Jupyter notebook.

        """
        return visualize.scene([self])

class Face(PlanarPolygon):
    """
    A :class:`PlanarPolygon` with an associated polarity. `Face.Positive` polarity
    follows the right hand rule, `Face.Negative` is inverted.

    >>> tri= Polygon2([Point2(0, 0), Point2(0, 2), Point2(1, 1)])
    >>> triangle = Face(Basis.xy, Face.Positive, tri)

    """
    Positive = 1
    Negative = -1

    def __init__(self, basis, direction, polygon):
        assert direction in [Face.Positive, Face.Negative]
        a = basis.normal().angle(Vector3.basis.x)
        if a == tau / 4:
            a = basis.normal().angle(Vector3.basis.y)
            if a == tau / 4:
                a = basis.normal().angle(Vector3.basis.z)
        inverted = a > tau / 4
        if inverted ^ (direction == Face.Negative):
            polygon = polygon.to_counterclockwise()
        else:
            polygon = polygon.to_clockwise()
        super().__init__(basis, polygon)
        self.direction = direction

    def simplified_projection(self):
        if isinstance(self.polygon, plane.Polygon) and self.polygon.is_convex():
            simple = [self.polygon]
        else:
            simple = decompose.trapezoidal(self.polygon.polygons)
        return [Face(self.basis, self.direction, p).project()[0] for p in simple]
