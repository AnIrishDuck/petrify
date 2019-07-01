"""
Creation of complex objects from humble building blocks:

:py:class:`Box` :
    A simple box.
:py:class:`Cylinder` :
    A cylinder rotated around an origin and axis.
:py:class:`PolygonExtrusion` :
    Extrusion of a :class:`space.PlanarPolygon` into a three-dimensional shape.
:py:class:`Spun` :
    A series of profiles spun around an axis and connected together.
:py:class:`Extrusion` :
    Complex layered objects with polygon slices.
:py:class:`Node` :
    Arbitrary construction of geometry via polygons.

All of the above classes subclass :py:class:`Node`, which allows object joining
via CSG union and difference operations.

"""
import math

from . import engines, plane, units, visualize
from .space import _pmap, Matrix, Point, Polygon, PlanarPolygon, Face, Basis, Vector
from .geometry import tau, valid_scalar

def perpendicular(axis):
    "Return a vector that is perpendicular to the given axis."
    if axis.x == 0 and axis.y == 0:
        return Vector(1, -1, 0)
    elif axis.z == 0:
        return Vector(-axis.y, axis.x, 0)
    else:
        return Vector(axis.y, axis.x, -2 * axis.x * axis.y)

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
    Box(Point(0, 0, 0), Vector(2, 1, 1))
    >>> (box + Vector(1, 0, 1)).envelope()
    Box(Point(1.0, 0.0, 1.0), Vector(1.0, 1.0, 1.0))

    To support unit operations via `pint`, multiplication and division by a
    scalar are also supported:

    >>> (box * 2).envelope()
    Box(Point(0, 0, 0), Vector(2, 2, 2))
    >>> (box / 2).envelope()
    Box(Point(0.0, 0.0, 0.0), Vector(0.5, 0.5, 0.5))
    >>> from petrify import u
    >>> (box * u.mm).units
    <Unit('millimeter')>

    """
    def __init__(self, polygons):
        self.polygons = polygons
        self.view_data = {}

    def view(self, **data):
        return View(self, **data)

    def __add__(self, other):
        if isinstance(other, Vector):
            return self.translate(other)
        else:
            n = Node(engines.csg.union(self.polygons, other.polygons))
            n.parts = [self, other]
            return n

    def __mul__(self, other):
        if isinstance(other, Vector):
            return self.scale(other)
        elif isinstance(other, Node):
            n = Node(engines.csg.intersect(self.polygons, other.polygons))
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
        n = Node(engines.csg.subtract(self.polygons, other.polygons))
        n.original = self
        n.removal = other
        return n

    @property
    def points(self):
        return [x for p in self.polygons for x in p.points]

    def envelope(self):
        """
        Returns the axis-aligned bounding box for this shape:

        >>> parallelogram = plane.Polygon([  \
            plane.Point(0, 0), \
            plane.Point(0, 1), \
            plane.Point(1, 2), \
            plane.Point(1, 1)  \
        ])
        >>> extruded = PolygonExtrusion(            \
            PlanarPolygon(Basis.xy, parallelogram), \
            Vector(0, 0, 1)                         \
        )
        >>> extruded.envelope()
        Box(Point(0, 0, 0), Vector(1, 2, 1))

        """
        origin = _pmap(Point, min, self.points)
        extent = _pmap(Point, max, self.points)
        return Box(origin, extent - origin)

    def mesh(self):
        import numpy as np
        import pythreejs as js

        wireframe = self.view_data.get('wireframe', False)

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

        geometry = js.BufferGeometry(
            attributes={
                'position': _ba(vertices),
                'normal': _ba(normals)
            },
        )

        if not wireframe:
            color = self.view_data.get('color', 'white')
            material = material=js.MeshLambertMaterial(color=color)
            return js.Mesh(geometry, material)
        else:
            color = self.view_data.get('color', '#00ff00')
            material = js.MeshBasicMaterial(color=color, wireframe=True)
            return js.Mesh(geometry, material)

    def render(self, **properties):
        """
        Create a `pythreejs`_ visualization of this geometry for use in
        interactive notebooks.

        .. _`pythreejs`: https://github.com/jupyter-widgets/pythreejs

        """
        return visualize.scene([self], **properties)

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

    def rotate(self, axis, theta):
        """ Rotate this geometry around the given `axis` vector by `theta` radians. """
        return Transformed(self, Matrix.rotate_axis(axis, theta))

    def rotate_at(self, origin, axis, theta):
        """ Rotate this geometry about the given `origin` and `axis` by `theta` radians. """
        return Transformed(self, Matrix.rotate_at(origin, axis, theta))

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
        self.nodes = nodes
        super().__init__([p for n in nodes if hasattr(n, 'polygons') for p in n.polygons])

    def flatten(self):
        return [child for n in self.nodes
                for child in (n.flatten() if isinstance(n, Collection) else [n])]

    def render(self, **properties):
        return visualize.scene(self.flatten(), **properties)

class View(Node):
    """
    Apply view properties to geometry.

    >>> v = View(Box(Point.origin, Vector(1, 1, 1)), wireframe=True)

    """
    def __init__(self, node, **data):
        self.node = node
        super().__init__(node.polygons)
        self.view_data = data

class Extrusion(Node):
    """
    A three-dimensional object built from rings of :class:`space.PlanarPolygon`
    objects with the same number of points at each ring:

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
    >>> object = Extrusion([                                \
        PlanarPolygon(Basis.xy, parallelogram),             \
        PlanarPolygon(Basis.xy + Vector(0, 0, 1), square),  \
    ])

    The rings must all have the same number of vertices. Quads are generated to
    connect each ring, and the bottom and top layers then complete the shape.

    `rings` :
        A list of :class:`space.PlanarPolygon` objects defining each ring of
        the final shape.

    """

    def __init__(self, slices):
        sizes = (
            tuple(len(poly.points) for poly in sl.polygon.polygons())
            for sl in slices
        )
        assert(len(set(sizes)) == 1)
        self.slices = slices

        super().__init__(self.generate_polygons())

    def construction(self):
        return Collection(self.slices)

    def generate_polygons(self):
        """ Calculates all polygons for this shape. """
        levels = [
            [
                *s.to_face(Face.Positive).project(exterior=True),
                *s.to_face(Face.Negative).project(exterior=False)
            ] for s in self.slices
        ]

        bottom = self.create_cap(self.slices[0], Face.Positive)
        middle = [
            p for la, lb in zip(levels, levels[1:])
            for a, b in zip(la, lb)
            for p in self.ring(a, b)
        ]
        top = self.create_cap(self.slices[-1], Face.Negative)

        return [*bottom, *middle, *top]

    def create_cap(self, slice, polarity):
        return Face(slice.basis, polarity, slice.polygon).simplified_projection()

    def ring(self, bottom, top):
        """ Builds a ring from two slices. """
        lines = list(zip(bottom.points, top.points))
        polygons =  [Polygon([la[1], lb[1], lb[0], la[0]]).simplify()
                     for la, lb in zip(lines, lines[1:] + [lines[0]])]
        return [p for p in polygons if p is not None]

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
        self.view_data = prior.view_data

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
        super().__init__(engines.csg.union(*(p.polygons for p in parts)))
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
        bz = Vector.basis.z
        bottom = PlanarPolygon(Basis.xy + bz * origin.z, footprint)
        top = PlanarPolygon(Basis.xy + bz * extent.z, footprint)

        super().__init__([bottom, top])

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
    >>> planar = PlanarPolygon(Basis.xy, triangle)
    >>> extruded = PolygonExtrusion(planar, Vector(0, 0, 1))

    `footprint` :
        a :py:class:`space.PlanarPolygon` object describing a the polygon
        that will be extruded in the given `direction`
    `direction` :
        A :class:`space.Vector` defining which direction the polygon will be
        linearly extruded into.

    """
    def __init__(self, footprint, direction):
        self.footprint = footprint
        self.bottom = self.footprint
        self.top = PlanarPolygon(footprint.basis + direction, footprint.polygon)

        super().__init__([self.bottom, self.top])

class Spun(Node):
    """
    A three-dimensional object built from two-dimensional profiles rotated uniformly around
    an axis:

    >>> axis = Vector.basis.z
    >>> start = Vector.basis.y
    >>> tri = plane.Polygon([   \
        plane.Point(0, 0),      \
        plane.Point(1, 1),      \
        plane.Point(0, 2)       \
    ])
    >>> spun = Spun(axis, start, [tri] * 5)

    The y-axis of the profile is used as the rotational axis when building the solid.

    """
    def __init__(self, axis, start, turns):
        self.axis = axis
        self.start = start
        assert(len(set(len(t.points) for t in turns)) == 1)
        self.turns = turns

        super().__init__(self.generate_polygons())

    def profile(self, polygon, angle):
        bx = self.start.rotate(self.axis, angle)
        return Polygon([
            (p.x * bx + p.y * self.axis).point()
            for p in polygon.points
        ])

    def profiles(self):
        steps = len(self.turns) - 1
        return [
            self.profile(polygon, tau * float(ix) / steps)
            for ix, polygon in enumerate(self.turns)
        ]

    def construction(self):
        return Collection(self.profiles())

    def generate_polygons(self):
        """ Calculates all polygons for this shape. """
        profiles = self.profiles()

        middle = [p
                  for a, b in zip(profiles, profiles[1:])
                  for p in self.rotation(a, b)]

        return middle

    def rotation(self, a, b):
        """ Builds a ring from two slices. """
        lines = list(zip(a.points, b.points))
        polygons = [Polygon([la[1], lb[1], lb[0], la[0]]).simplify()
                    for la, lb in zip(lines, lines[1:] + [lines[0]])]
        return [p for p in polygons if p is not None]

class Cylinder(PolygonExtrusion):
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
    `radius` :
        the radius of the cylinder.
    `segments` :
        the number of quads to use when approximating the cylinder.

    """

    def __init__(self, origin, axis, radius, segments=10):
        self.origin = origin
        self.axis = axis
        self.radius = radius

        angles = list(tau * float(a) / segments for a in range(segments))
        circle = plane.Polygon([
            plane.Point(math.cos(theta) * radius, math.sin(theta) * radius)
            for theta in angles
        ])

        bx = perpendicular(axis).normalized()
        by = bx.cross(axis).normalized()
        bottom = PlanarPolygon(Basis(origin, bx, by), circle)
        super().__init__(bottom, axis)

    def height(self):
        """ The height of this cylinder along its `axis`. """
        return self.axis.magnitude()
