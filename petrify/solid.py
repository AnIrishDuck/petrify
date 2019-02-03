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
    def __init__(self, points, dz):
        self.points = points
        self.dz = dz

    def project(self, projection):
        return [projection.convert(p, self.dz) for p in self.points]

class Extrusion:
    def __init__(self, projection, slices):
        self.projection = projection
        assert(len(set(len(sl.points) for sl in slices)) == 1)
        self.slices = slices

        ps = self.polygons()
        self.csg = core.CSG.fromPolygons(ps)

    def polygons(self):
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
        bottom = a.project(self.projection)
        top = b.project(self.projection)
        lines = list(zip(bottom, top))
        return [[la[0], lb[0], lb[1], la[1]]
                 for la, lb in zip(lines, lines[1:] + [lines[0]])]

class Node:
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
        def scaled(v):
            return Vector3(v.x * scale.x, v.y * scale.y, v.z * scale.z)
        return self.transform(scaled)

    def translate(self, delta):
        def scaled(v):
            return Vector3(v.x + delta.x, v.y + delta.y, v.z + delta.z)
        return self.transform(scaled)

    def transform(self, f):
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
        polygons = self.csg.toPolygons()
        save_polys_to_stl_file(polygons, path)

class Union(Node):
    def __init__(self, parts):
        whole = parts[0].csg
        for part in parts[1:]:
            whole = whole.union(part)
        self.parts = parts
        self.csg = whole

class Box(Extrusion, Node):
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
