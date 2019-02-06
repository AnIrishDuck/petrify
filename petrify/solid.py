import math

from .stl import save_polys_to_stl_file, read_polys_from_stl_file
from .euclid import Vector2, Vector3, Matrix3, Matrix4
from csg import core, geom

tau = math.pi * 2

def perpendicular(axis):
    "Return a vector that is perpendicular to the given axis."
    if axis.x == 0 and axis.y == 0:
        return Vector3(1, -1, 0)
    elif axis.z == 0:
        return Vector3(-axis.y, axis.x, 0)
    else:
        return Vector3(axis.y, axis.x, -2 * axis.x * axis.y)

def vertex(vector):
    return geom.Vertex(geom.Vector(vector.x, vector.y, vector.z))

class Projection:
    """
    Used for building solids from slices of two-dimensional geometry along a
    given z-axis.

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
        return Vector3(v.x, v.y, v.z)

class Slice:
    """ A slice of two-dimensional geometry associated with a z-level. """
    def __init__(self, points, dz):
        self.points = points
        self.dz = dz

    def project(self, projection):
        return [projection.convert(p, self.dz) for p in self.points]

class Extrusion:
    """
    A three-dimensional object built from varying height slices of 2d polygons.

    The slices must currently all have the same number of vertices. Quads are
    generated to connect each layer, and the bottom and top layers then complete
    the shape.

    Parameters
    ----------
    projection :
        A :class:`Projection` defining the basis for the projected shape.
    slices :
        A list of :class:`Slice` objects defining each layer of the final shape.

    """

    def __init__(self, projection, slices):
        self.projection = projection
        assert(len(set(len(sl.points) for sl in slices)) == 1)
        self.slices = slices

        ps = self.polygons()
        self.csg = core.CSG.fromPolygons(ps)

    def polygons(self):
        """ Returns all polygons from this shape. """
        bottom = self.slices[0].project(self.projection)
        top = self.slices[-1].project(self.projection)

        def i(p): return list(reversed(p))
        ix = len(self.slices[0].points)
        middle = [i(p) for a, b in zip(self.slices, self.slices[1:])
                  for p in self.ring(a, b)]
        polygons = [bottom] + middle + [i(top)]

        return [
            geom.Polygon([vertex(v) for v in polygon])
            for polygon in polygons
        ]

    def ring(self, a, b):
        """ Builds a ring from two slices. """
        bottom = a.project(self.projection)
        top = b.project(self.projection)
        lines = list(zip(bottom, top))
        return [[la[0], lb[0], lb[1], la[1]]
                 for la, lb in zip(lines, lines[1:] + [lines[0]])]

class Node:
    """
    Convenience class for performing CSG operations on geometry.

    All instances of this class can be added and subtracted via the built-in
    `__add__` and `__sub__` methods:

    >>> a = Box(Vector3(0, 0, 0), Vector3(1, 1, 1))
    >>> b = Box(Vector3(0, 0, 0.5), Vector3(1, 1, 1))
    >>> a + b # union
    >>> a - b # subtraction

    """
    def __init__(self, csg):
        self.csg = csg

    def __add__(self, other):
        n = Node(self.csg.union(other.csg))
        n.left = self
        n.right = other
        return n

    def __sub__(self, other):
        n = Node(self.csg.subtract(other.csg))
        n.left = self
        n.right = other
        return n

    def scale(self, scale):
        """ Scale this geometry by the provided `scale` vector. """
        def scaled(v):
            return Vector3(v.x * scale.x, v.y * scale.y, v.z * scale.z)
        return self.transform(scaled)

    def translate(self, delta):
        """ Translate this geometry by the provided `translate` vector. """
        def scaled(v):
            return Vector3(v.x + delta.x, v.y + delta.y, v.z + delta.z)
        return self.transform(scaled)

    def rotate(self, axis, theta):
        """ Rotate this geometry around the given `axis` vector by `theta` radians. """

    def transform(self, f):
        """ Map the specified function `f` across all vertices. """
        polygons = self.csg.toPolygons()

        def t(vertex):
            v = f(vertex.pos)
            return geom.Vertex(geom.Vector(v.x, v.y, v.z))

        scaled = [
            geom.Polygon([t(v) for v in polygon.vertices])
            for polygon in polygons
        ]
        return Node(core.CSG.fromPolygons(scaled))

    def to_stl(self, path):
        """ Save this shape to an STL-formatted file. """
        polygons = self.csg.toPolygons()
        save_polys_to_stl_file(polygons, path)

class Union(Node):
    """ Defines a union of a list of `parts` """
    def __init__(self, parts):
        whole = parts[0].csg
        for part in parts[1:]:
            whole = whole.union(part)
        self.parts = parts
        self.csg = whole

class Box(Extrusion, Node):
    """
    A simple three-dimensional box constructed from a given `origin` and `size`
    vector.

    """

    def __init__(self, origin, size):
        self.origin = origin
        self.extent = extent = origin + size

        footprint = [Vector2(x, y) for x, y in [
            [origin.x, origin.y],
            [origin.x, extent.y],
            [extent.x, extent.y],
            [extent.x, origin.y]
        ]]
        bottom = Slice(footprint, origin.z)
        top = Slice(footprint, extent.z)

        project = Projection(
            Vector3(0, 0, 0),
            Vector3(1, 0, 0),
            Vector3(0, 1, 0),
            Vector3(0, 0, 1)
        )
        super().__init__(project, [bottom, top])

    def size(self):
        return self.extent - self.origin

class Cylinder(Extrusion, Node):
    """
    A three-dimensional cylinder extruded along the given `axis`. The magnitude
    of the axis is the height of the cylinder.

    The actual cylinder is constructed from many `segments` of quads to simulate
    a circular shape.

    """

    def __init__(self, origin, axis, radius, segments=10):
        self.origin = origin
        self.axis = axis
        self.radius = radius

        angles = list(tau * float(a) / segments for a in range(segments))
        footprint = [
            Vector2(math.cos(theta) * radius, math.sin(theta) * radius)
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
