"""
Creation of complex objects from humble building blocks.

:py:class:`Box`, :py:class:`Cylinder` and :py:class:`Extrusion` are all instances
of :py:class:`Node`, which allows object joining via CSG union and difference
operations.

:py:class:`Extrusion` can also be used to create complex geometries from slices
of arbitrary planar polygons:

>>> parallelogram = [
    plane.Point(0, 0),
    plane.Point(0, 1),
    plane.point(1, 2),
    plane.point(1, 1)
]
>>> square = [
    plane.Point(0, 0),
    plane.Point(0, 1),
    plane.point(1, 1),
    plane.point(1, 0)
]
>>> Extrusion(Projection.unit, [
    Slice(parallelogram, 0)
    Slice(square, 1)
])

"""
import math
from csg import core, geom

from . import plane
from .stl import save_polys_to_stl_file, read_polys_from_stl_file
from .space import Matrix, Point, Polygon, Vector
from .geometry import tau

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
    given z-axis.

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
    """ A slice of two-dimensional geometry associated with a z-level. """
    def __init__(self, points, dz):
        self.points = points
        self.dz = dz

    def project(self, projection):
        return [projection.convert(p, self.dz) for p in self.points]

class Extrusion:
    """
    A three-dimensional object built from varying height :py:class:`Slice`
    polygons.

    The slices must currently all have the same number of vertices. Quads are
    generated to connect each layer, and the bottom and top layers then complete
    the shape.

    `projection` :
        A :class:`Projection` defining the basis for the projected shape.
    `slices` :
        A list of :class:`Slice` objects defining each layer of the final shape.

    """

    def __init__(self, projection, slices):
        self.projection = projection
        assert(len(set(len(sl.points) for sl in slices)) == 1)
        self.slices = slices

        super().__init__(self.generate_polygons())

    def generate_polygons(self):
        """ Returns all polygons from this shape. """
        bottom = self.slices[0].project(self.projection)
        top = self.slices[-1].project(self.projection)

        def i(p): return list(reversed(p))
        ix = len(self.slices[0].points)
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
    return [from_csg_polygon(p) for p in _csg.toPolygons()]

def to_pycsg(polygons):
    def to_csg_polygon(polygon):
        vertices = [geom.Vertex(geom.Vector(p.x, p.y, p.z)) for p in polygon.points]
        return geom.Polygon(vertices)
    return core.CSG.fromPolygons([to_csg_polygon(p) for p in polygons])

class Node:
    """
    Convenience class for performing CSG operations on geometry.

    All instances of this class can be added and subtracted via the built-in
    `__add__` and `__sub__` methods:

    >>> a = Box(Vector(0, 0, 0), Vector(1, 1, 1))
    >>> b = Box(Vector(0, 0, 0.5), Vector(1, 1, 1))
    >>> a + b # union
    >>> a - b # difference

    """
    def __init__(self, polygons):
        self.polygons = polygons

    def __add__(self, other):
        n = Node(from_pycsg(self.pycsg.union(other.pycsg)))
        n.left = self
        n.right = other
        return n

    def __sub__(self, other):
        n = Node(from_pycsg(self.pycsg.subtract(other.pycsg)))
        n.left = self
        n.right = other
        return n

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

    def to_stl(self, path):
        """ Save this shape to an STL-formatted file. """
        save_polys_to_stl_file(self.pycsg.toPolygons(), path)

class Transformed(Node):
    """ Geometry that has had a matrix transform applied to it. """
    def __init__(self, prior, matrix):
        self.prior = prior
        self.matrix = matrix

        polygons = [
            Polygon([matrix * point for point in polygon.points])
            for polygon in prior.polygons
        ]
        super().__init__(polygons)

class Union(Node):
    """ Defines a union of a list of `parts` """
    def __init__(self, parts):
        whole = parts[0].pycsg
        for part in parts[1:]:
            whole = whole.union(part.pycsg)
        super().__init__(from_pycsg(whole))
        self.parts = parts

class Box(Extrusion, Node):
    """
    A simple three-dimensional box.

    `origin` :
        a :class:`petrify.space.Point` defining the origin of this box.
    `size` :
        a :class:`petrify.space.Vector` of the box's size.

    """

    def __init__(self, origin, size):
        self.origin = origin
        self.extent = extent = origin + size

        footprint = [plane.Point(x, y) for x, y in [
            [origin.x, origin.y],
            [origin.x, extent.y],
            [extent.x, extent.y],
            [extent.x, origin.y]
        ]]
        bottom = Slice(footprint, origin.z)
        top = Slice(footprint, extent.z)

        project = Projection(
            Vector(0, 0, 0),
            Vector(1, 0, 0),
            Vector(0, 1, 0),
            Vector(0, 0, 1)
        )
        super().__init__(project, [bottom, top])

    def size(self):
        return self.extent - self.origin

class PolygonExtrusion(Extrusion, Node):
    """

    Extrusion of a simple two-dimensional polygon into three-dimensional space.

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
        top = Slice(footprint, 1)
        super().__init__(projection, [bottom, top])

class Cylinder(PolygonExtrusion):
    """
    A three-dimensional cylinder extruded along the given `axis`.

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
        footprint = [
            plane.Point(math.cos(theta) * radius, math.sin(theta) * radius)
            for theta in angles
        ]

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

    def length(self):
        return self.axis.magnitude()
