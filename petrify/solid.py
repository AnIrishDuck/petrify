"""
Creation of complex objects from humble building blocks:

:py:class:`Box` :
    A simple box.
:py:class:`Cylinder` :
    A cylinder rotated around an origin and axis.
:py:class:`PolygonExtrusion` :
    Extrusion of a polygon into a three-dimensional shape.
:py:class:`Sweep` :
    Sweep a series of polygons along a three-dimensional line.
:py:class:`Extrusion` :
    Complex layered objects with polygon slices.
:py:class:`External` :
    An external mesh loaded from an STL file.
:py:class:`Node` :
    Arbitrary construction of geometry via polygons.

All of the above classes subclass :py:class:`Node`, which allows object joining
via CSG union and difference operations.

"""
import math
from csg import core, geom

from . import plane, units
from .space import Matrix, Point, Polygon, Vector
from .geometry import tau, valid_scalar

def perpendicular(axis):
    "Return a vector that is perpendicular to the given axis."
    if axis.x == 0 and axis.y == 0:
        return Vector(1, -1, 0)
    elif axis.z == 0:
        return Vector(-axis.y, axis.x, 0)
    else:
        return Vector(axis.y, axis.x, -2 * axis.x * axis.y)

class Projection:
    """
    Used for building solids from slices of two-dimensional geometry along a
    given z-axis:

    >>> project = Projection( \
        Point.origin,         \
        Vector(1, 1, 0),      \
        Vector(0, 1, 1),      \
        Vector(1, 0, 1)       \
    )
    >>> project.convert(plane.Point(1, 1), 1)
    Point(2, 2, 2)

    The basis vectors `bx`, `by` are multiplied by the corresponding `x` and `y`
    scalars of a :py:class:`Slice` points, and the slice height is multiplied by
    `bz`. All components are added together to get the final point in
    three-dimensional space.

    """
    def __init__(self, origin, bx, by, bz):
        self.origin = origin
        self.bx = bx
        self.by = by
        self.bz = bz

    def convert(self, point, dz):
        tx = point.x * self.bx
        ty = point.y * self.by
        tz = dz * self.bz

        v = self.origin + tx + ty + tz
        return Point(v.x, v.y, v.z)

Projection.unit = Projection(
    Point.origin,
    Vector.basis.x,
    Vector.basis.y,
    Vector.basis.z
)

class Slice:
    """
    A slice of two-dimensional geometry associated with a z-level:

    >>> triangle = plane.Polygon([  \
        plane.Point(0, 0),          \
        plane.Point(0, 2),          \
        plane.Point(1, 1)           \
    ])
    >>> s = Slice(triangle, 1)
    >>> s.project(Projection.unit)
    [Point(0, 0, 1), Point(0, 2, 1), Point(1, 1, 1)]

    """
    def __init__(self, polygon, dz):
        self.polygon = polygon
        self.dz = dz

    def project(self, projection):
        return [projection.convert(p, self.dz) for p in self.polygon.points]

class Node:
    """
    Convenience class for performing CSG operations on geometry.

    All instances of this class can be added and subtracted via the built-in
    `__add__` and `__sub__` methods:

    >>> a = Box(Vector(0, 0, 0), Vector(1, 1, 1))
    >>> b = Box(Vector(0, 0, 0.5), Vector(1, 1, 1))
    >>> union = a + b
    >>> difference = a - b

    All nodes also support scaling and translation via vectors:

    >>> box = Box(Vector(0, 0, 0), Vector(1, 1, 1))
    >>> (box * Vector(2, 1, 1)).envelope()
    Box(Vector(0, 0, 0), Vector(2, 1, 1))
    >>> (box + Vector(1, 0, 1)).envelope()
    Box(Vector(1.0, 0.0, 1.0), Vector(1.0, 1.0, 1.0))

    To support unit operations via `pint`, multiplication and division by a
    scalar are also supported:

    >>> (box * 2).envelope()
    Box(Vector(0, 0, 0), Vector(2, 2, 2))
    >>> (box / 2).envelope()
    Box(Vector(0.0, 0.0, 0.0), Vector(0.5, 0.5, 0.5))
    >>> from petrify import u
    >>> (box * u.mm).units
    <Unit('millimeter')>

    """
    def __init__(self, polygons):
        self.polygons = polygons

    def __add__(self, other):
        if isinstance(other, Vector):
            return self.translate(other)
        else:
            n = Node(from_pycsg(self.pycsg.union(other.pycsg)))
            n.parts = [self, other]
            return n

    def __mul__(self, other):
        if isinstance(other, Vector):
            return self.scale(other)
        elif isinstance(other, Node):
            n = Node(from_pycsg(self.pycsg.intersect(other.pycsg)))
            n.parts = [self, other]
            return n
        elif valid_scalar(other):
            return self * Vector(other, other, other)
        else:
            return NotImplemented
    __rmul__ = __mul__

    def __truediv__(self, other):
        if valid_scalar(other):
            return self * Vector(1 / other, 1 / other, 1 / other)
        else:
            return NotImplemented

    def __sub__(self, other):
        n = Node(from_pycsg(self.pycsg.subtract(other.pycsg)))
        n.original = self
        n.removal = other
        return n

    def envelope(self):
        """
        Returns the axis-aligned bounding box for this shape:

        >>> parallelogram = plane.Polygon([  \
            plane.Point(0, 0), \
            plane.Point(0, 1), \
            plane.Point(1, 2), \
            plane.Point(1, 1)  \
        ])
        >>> extruded = PolygonExtrusion(Projection.unit, parallelogram, 1)
        >>> extruded.envelope()
        Box(Vector(0, 0, 0), Vector(1, 2, 1))

        """
        points = [x for p in self.polygons for x in p.points]
        origin = Vector(
            min(p.x for p in points),
            min(p.y for p in points),
            min(p.z for p in points)
        )
        extent = Vector(
            max(p.x for p in points),
            max(p.y for p in points),
            max(p.z for p in points)
        )
        return Box(origin, extent - origin)

    def visualize(self):
        """
        Create a `pythreejs`_ visualization of this geometry for use in
        interactive notebooks.

        .. _`pythreejs`: https://github.com/jupyter-widgets/pythreejs

        """
        import numpy as np
        import pythreejs as js

        def triangles(polygon):
            points = polygon.points
            return [(points[0], points[ix], points[ix + 1])
                    for ix in range(1, len(polygon.points) - 1)]

        def _ba(vs):
            points = np.array(vs, dtype=np.float32)
            return js.BufferAttribute(array=points, normalized=False)

        vertices = [
            list(p.xyz) for polygon in self.polygons
            for t in triangles(polygon)
            for p in t
        ]
        normals = [
            list(polygon.plane.normal.xyz) for polygon in self.polygons
            for t in triangles(polygon)
            for p in t
        ]

        return js.BufferGeometry(
            attributes={
                'position': _ba(vertices),
                'normal': _ba(normals)
            },
        )

    def as_unit(self, unit):
        """
        Declare a unit for unitless geometry:

        >>> Box(Vector(0, 0, 0), Vector(1, 1, 1)).as_unit('inch').units
        <Unit('inch')>

        """
        return units.assert_lengthy(1 * units.parse_unit(unit)) * self

    def scale(self, scale):
        """ Scale this geometry by the provided `scale` vector. """
        return Transformed(self, Matrix.scale(*scale.xyz))

    def translate(self, delta):
        """ Translate this geometry by the provided `translate` vector. """
        return Transformed(self, Matrix.translate(*delta.xyz))

    def rotate_around(self, theta, axis):
        """ Rotate this geometry around the given `axis` vector by `theta` radians. """
        return Transformed(self, Matrix.rotate_axis(theta, axis))

    @property
    def pycsg(self):
        return to_pycsg(self.polygons)

class Collection(Node):
    """
    Collection of multiple objects. Self-intersection is unsupported, but
    lack of intersection is not enforced:

    >>> c = Collection([ \
        Box(Point.origin, Vector(1, 1, 1)),     \
        Box(Point(0, 5, 0), Vector(1, 1, 1))    \
    ])
    """
    def __init__(self, nodes):
        super().__init__([p for n in nodes for p in n.polygons])

class Extrusion(Node):
    """
    A three-dimensional object built from varying height :py:class:`Slice`
    polygon layers:

    >>> parallelogram = plane.Polygon([  \
        plane.Point(0, 0), \
        plane.Point(0, 1), \
        plane.Point(1, 2), \
        plane.Point(1, 1)  \
    ])
    >>> square = plane.Polygon([    \
        plane.Point(0, 0),          \
        plane.Point(0, 1),          \
        plane.Point(1, 1),          \
        plane.Point(1, 0)           \
    ])
    >>> object = Extrusion(Projection.unit, [ \
        Slice(parallelogram, 0),     \
        Slice(square, 1)             \
    ])

    The slices must all have the same number of vertices. Quads are
    generated to connect each layer, and the bottom and top layers then complete
    the shape.

    `projection` :
        A :class:`Projection` defining the basis for the projected shape.
    `slices` :
        A list of :class:`Slice` objects defining each layer of the final shape.

    """

    def __init__(self, projection, slices):
        self.projection = projection
        assert(len(set(len(sl.polygon.points) for sl in slices)) == 1)
        self.slices = slices

        super().__init__(self.generate_polygons())

    def generate_polygons(self):
        """ Returns all polygons from this shape. """
        bottom = self.slices[0].project(self.projection)
        top = self.slices[-1].project(self.projection)

        def i(p): return list(reversed(p))
        middle = [i(p) for a, b in zip(self.slices, self.slices[1:])
                  for p in self.ring(a, b)]
        polygons = [bottom] + middle + [i(top)]

        return [Polygon(p) for p in polygons]

    def ring(self, a, b):
        """ Builds a ring from two slices. """
        bottom = a.project(self.projection)
        top = b.project(self.projection)
        lines = list(zip(bottom, top))
        return [[la[0], lb[0], lb[1], la[1]]
                 for la, lb in zip(lines, lines[1:] + [lines[0]])]

    @property
    def bottom(self):
        """ The bottom polygon of this extrusion. """
        return self.polygons[0]

    @property
    def top(self):
        """ The top polygon of this extrusion. """
        return self.polygons[-1]

def from_pycsg(_csg):
    def from_csg_polygon(csg):
        points = [Point(v.pos.x, v.pos.y, v.pos.z) for v in csg.vertices]
        return Polygon(points)
    return [from_csg_polygon(p) for p in (_csg if isinstance(_csg, list) else _csg.toPolygons())]

def to_pycsg(polygons):
    def to_csg_polygon(polygon):
        vertices = [geom.Vertex(geom.Vector(p.x, p.y, p.z)) for p in polygon.points]
        return geom.Polygon(vertices)
    return core.CSG.fromPolygons([to_csg_polygon(p) for p in polygons])

class Transformed(Node):
    """
    Geometry that has had a matrix transform applied to it.

    You probably should use methods on :py:class:`Node` instead of instantiating
    this class directly.

    """
    def __init__(self, prior, matrix):
        self.prior = prior
        self.matrix = matrix

        polygons = [
            Polygon([matrix * point for point in polygon.points])
            for polygon in prior.polygons
        ]
        super().__init__(polygons)

class Union(Node):
    """
    Defines a union of a list of `parts`:

    >>> many = Union([                         \
        Box(Point(0, 0, 0), Vector(10, 1, 1)), \
        Box(Point(0, 0, 0), Vector(1, 10, 1)), \
        Box(Point(0, 0, 0), Vector(1, 1, 10)), \
    ])

    """
    def __init__(self, parts):
        whole = parts[0].pycsg
        for part in parts[1:]:
            whole = whole.union(part.pycsg)
        super().__init__(from_pycsg(whole))
        self.parts = parts

class Box(Extrusion):
    """
    A simple three-dimensional box:

    >>> cube = Box(Point.origin, Vector(1, 1, 1))

    `origin` :
        a :class:`petrify.space.Point` defining the origin of this box.
    `size` :
        a :class:`petrify.space.Vector` of the box's size.

    """

    def __init__(self, origin, size):
        self.origin = origin
        self.extent = extent = origin + size

        footprint = plane.Polygon([plane.Point(x, y) for x, y in [
            [origin.x, origin.y],
            [origin.x, extent.y],
            [extent.x, extent.y],
            [extent.x, origin.y]
        ]])
        bottom = Slice(footprint, origin.z)
        top = Slice(footprint, extent.z)

        project = Projection(
            Vector(0, 0, 0),
            Vector(1, 0, 0),
            Vector(0, 1, 0),
            Vector(0, 0, 1)
        )
        super().__init__(project, [bottom, top])

    def __repr__(self):
        return "Box({0!r}, {1!r})".format(self.origin, self.size())

    def size(self):
        return self.extent - self.origin

class PolygonExtrusion(Extrusion):
    """

    Extrusion of a simple two-dimensional polygon into three-dimensional space:

    >>> triangle = plane.Polygon([  \
        plane.Point(0, 0),          \
        plane.Point(0, 2),          \
        plane.Point(1, 1)           \
    ])
    >>> extruded = PolygonExtrusion(Projection.unit, triangle, 1)

    `projection` :
        a :py:class:`Projection` that defines how to transform the points of the
        polygon.
    `footprint` :
        a list of :py:class:`plane.Point` objects describing a convex polygon
        that will be extruded along the given `projection`
    `height` :
        the final object will join two :py:class:`Slice` polygons: one at `z=0`
        and one at `z=height`

    """
    def __init__(self, projection, footprint, height):
        self.footprint = footprint
        self.height = height

        bottom = Slice(footprint, 0)
        top = Slice(footprint, height)
        super().__init__(projection, [bottom, top])

class Sweep(Extrusion):
    """
    Create a solid from pairs of polygons swept along an arbitrary
    three-dimensional path. The basis for each polygon is constructed from
    combining path normals and a pre-provided basis vector that defines a
    uniform y-axis:

    >>> radius = 0.25
    >>> angles = [tau * float(a) / 10 for a in range(10)]
    >>> circle = plane.Polygon([ \
        plane.Point(math.cos(theta) * radius, math.sin(theta) * radius) \
        for theta in angles \
    ])
    >>> circles = [ \
        (Point(1, 0, 0), circle), \
        (Point(1, 1, 0), circle * plane.Vector(2, 2)), \
        (Point(0, 1, 0), circle)  \
    ]
    >>> angle = Sweep(circles, Vector.basis.z)


    .. warning::
        This code currently has no way of detecting self-intersection, which
        should be avoided.

    """

    class Projection:
        def __init__(self, path, by):
            self.by = by
            self.origins = [point for point, _ in path]
            vectors = [b - a for a, b in zip(self.origins, self.origins[1:])]
            z = Vector(0, 0, 0)
            self.normals = [
                (a + b) for a, b in zip((z, *vectors), (*vectors, z))
            ]

        def convert(self, point, dz):
            origin = self.origins[dz]
            bx = self.normals[dz].cross(self.by).normalized()
            v = origin + (point.x * bx) + (point.y * self.by)
            return Point(*v.xyz)

    def __init__(self, path, by):
        self.path = path
        self.by = by
        project = Sweep.Projection(self.path, self.by)
        slices = [
            Slice(footprint, ix)
            for ix, (_, footprint) in enumerate(path)
        ]
        super().__init__(project, slices)

class Cylinder(Extrusion):
    """
    A three-dimensional cylinder extruded along the given `axis`:

    >>> axle = Cylinder(Point.origin, Vector.basis.y * 10, 1.0)

    The actual cylinder is approximated by creating many `segments` of quads to
    simulate a circular shape.

    `origin` :
        a :class:`petrify.space.Point` defining the origin of this cylinder.
    `axis` :
        a :class:`petrify.space.Vector` that defines the axis the cylinder will
        be "spun about". The magnitude of the axis is the height of the cylinder.
    `segments` :
        the number of quads to use when approximating the cylinder.

    """

    def __init__(self, origin, axis, radius, segments=10):
        self.origin = origin
        self.axis = axis
        self.radius = radius

        angles = list(tau * float(a) / segments for a in range(segments))
        footprint = plane.Polygon([
            plane.Point(math.cos(theta) * radius, math.sin(theta) * radius)
            for theta in angles
        ])

        bottom = Slice(footprint, 0)
        top = Slice(footprint, 1)

        bx = perpendicular(axis)
        by = bx.cross(axis)
        project = Projection(
            origin,
            bx.normalized(),
            by.normalized(),
            axis
        )
        super().__init__(project, [bottom, top])

    def height(self):
        """ The height of this cylinder along its `axis`. """
        return self.axis.magnitude()
