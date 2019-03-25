"""
**Experimental** SVG support.

This currently only works with SVG paths devoid of problematic constructions:

- usage of fill-rule resulting in a single non-terminated (with the `Z` command)
  path resulting in unfilled areas.
- motion commands that move the "pen" without terminating the path.

Its current primary three-dimensional purpose is generating
:py:class:`petrify.solid.PathExtrusion` objects.

"""
from svg.path import parse_path, Line, CubicBezier, QuadraticBezier, Arc
from .. import units
from ..geometry import valid_scalar
from ..plane import Matrix, Point, Polygon
from ..decompose import trapezoidal
from ..solid import Node, PolygonExtrusion, Union
import re
import xml.sax

class PathExtrusion(Node):
    """
    A SVG path extruded into three-dimensional space.

    >>> from petrify import u
    >>> from petrify.space import Plane, Point, Vector
    >>> from petrify.solid import Projection
    >>> paths = SVG.read('tests/fixtures/example.svg', u.inches / (90 * u.file))
    >>> box = paths['rect'].m_as(u.inches)
    >>> plane = Plane(Vector.basis.z, Point.origin)
    >>> example = PathExtrusion(box, 1.0, Projection.unit)

    """
    def __init__(self, path, height, projection):
        path = path.polygons()
        interior = []
        exterior = []

        for ix, polygon in enumerate(path):
            if not polygon.clockwise():
                polygon = polygon.inverted()
            first = polygon.points[0]
            trapezoids = trapezoidal(polygon.points)
            others = path[:ix] + path[ix + 1:]
            if any(other.contains(first) for other in others):
                interior.extend(trapezoids)
            else:
                exterior.extend(trapezoids)

        interior = Union(
            [PolygonExtrusion(projection, p, height + 1) for p in interior]
        )
        exterior = Union(
            [PolygonExtrusion(projection, p, height) for p in exterior]
        )

        super().__init__((exterior - interior).polygons)

exp = re.compile('(.*)\((.*)\)')
def parse_transform(s):
    # see https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/transform
    # especially for the matrix type
    name, params = exp.match(s).groups()
    params = [float(v) for v in params.split(',')]
    if name == 'matrix':
        a, b, c, d, e, f = params
        # a c e
        # b d f
        # 0 0 1
        return Matrix.from_values(a, b, 0, c, d, 0, e, f, 1)
    elif name == 'translate':
        return Matrix.translate(*params)
    elif name == 'scale':
        return Matrix.scale(*params)
    elif name == 'rotate':
        if len(params) == 1:
            return Matrix.rotate(*params)
        else:
            angle, x, y = params
            return Matrix.translate(-x, -y) * Matrix.rotate(angle) * Matrix.rotate(x, y)

def from_complex(v):
    return Point(v.real, v.imag)

lines = [Line, CubicBezier, QuadraticBezier, Arc]
class Path:
    def __init__(self, transforms, data):
        self.transforms = transforms
        self.data = data

        self.transform = Matrix.identity()
        for transform in self.transforms:
            self.transform *= transform

    def __mul__(self, f):
        if not valid_scalar(f): return NotImplemented
        return Path([Matrix.scale(f, f), *self.transforms], self.data)
    __rmul__ = __mul__

    def parse(self):
        return parse_path(self.data)

    def t(self, point):
        return self.transform * point

    def polygons(self):
        parsed = self.parse()
        polygons = []
        current = []
        for ix in range(len(parsed)):
            command = parsed[ix]
            if any(isinstance(command, T) for T in lines):
                current.append(self.t(from_complex(command.end)))
            else:
                if current: polygons.append(current)
                current = [self.t(from_complex(command.start))]

        if current: polygons.append(current)

        return [Polygon(p) for p in polygons]

class Handler(xml.sax.ContentHandler):
    def __init__(self, scale):
        self.stack = []
        self.scale = units.conversion(scale)
        self.paths = {}

    def startElement(self, tag, attributes):
        transform = None
        if 'transform' in attributes:
            transform = attributes['transform']
        if tag == 'g':
            self.stack.append(transform)
        if tag == 'path':
            transforms = list(t for t in self.stack if t is not None)
            if transform: transforms.append(transform)
            transforms = [parse_transform(t) for t in transforms]
            path = Path(transforms, attributes['d'])
            x = path * units.u.file
            self.paths[attributes['id']] = path * units.u.file * self.scale

    def endElement(self, tag):
        if tag == 'g':
            self.stack.pop()

class SVG:
    @classmethod
    def read(cls, path, scale):
        parser = xml.sax.make_parser()
        svg = Handler(scale)
        parser.setContentHandler(svg)
        parser.parse(path)
        return svg.paths
