from stl import save_polys_to_stl_file, read_polys_from_stl_file
from csg import core, geom

import math
import os
import subprocess

tau = math.pi * 2

class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def positive():
        return Vector(math.abs(self.x), math.abs(self.y), math.abs(self.z))

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, v):
        return Vector(self.x * v, self.y * v, self.z * v)

    def __truediv__(self, v):
        return self * (1.0 / v)

    def __rmul__(self, v):
        return Vector(self.x * v, self.y * v, self.z * v)

    def __repr__(self):
        return "".join([str(s) for s in ["Point(", self.x, ",", self.y, ",", self.z, ")"]])

    def magnitude(self):
        "Magnitude of this vector."
        return math.sqrt(self.dot(self))

    def dot(self, other):
        "Dot product of this vector with another vector."
        return self.x * other.x + self.y * other.y + self.z * other.z

    def angle(self, other):
        "Angle between this vector and the other vector in radians."
        scale = self.magnitude() * other.magnitude()
        return math.acos(self.dot(other) / scale)

    def perpendicular(self):
        "Return a vector that is perpendicular to this one."
        if self.x == 0 and self.y == 0:
            return Vector(1, -1, 0)
        elif self.z == 0:
            return Vector(-self.y, -self.x, 1)
        else:
            return Vector(self.y, self.x, -2 * self.x * self.y)

    def cross(self, other):
        "Cross product of this vector with another vector."
        return Vector(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def unit(self):
        """
        Returns a vector with the same direction but unit (1) magnitude.

        """
        return self / self.magnitude()

    def csg(self):
        return geom.Vector(self.x, self.y, self.z)

    def vertex(self):
        return geom.Vertex(self.csg())

class PlanarPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

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
        return Vector(v.x, v.y, v.z)

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
            geom.Polygon([v.vertex() for v in polygon])
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
            return Vector(v.x * scale.x, v.y * scale.y, v.z * scale.z)
        return self.transform(scaled)

    def translate(self, delta):
        def scaled(v):
            return Vector(v.x + delta.x, v.y + delta.y, v.z + delta.z)
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

        footprint = [PlanarPoint(x, y) for x, y in [
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

class Cylinder(Extrusion, Node):
    def __init__(self, origin, axis, radius, segments=10):
        self.origin = origin
        self.axis = axis
        self.radius = radius

        angles = list(tau * float(a) / segments for a in range(segments))
        footprint = [
            PlanarPoint(math.cos(theta) * radius, math.sin(theta) * radius)
            for theta in angles
        ]

        bottom = Slice(footprint, 0)
        top = Slice(footprint, 1)

        bx = axis.perpendicular()
        by = bx.cross(axis)
        project = Projection(
            origin,
            bx.unit(),
            by.unit(),
            axis
        )
        super().__init__(project, [bottom, top])

    def length(self):
        return self.axis.magnitude()
