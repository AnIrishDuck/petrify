from svg.path import parse_path, Line, CubicBezier, QuadraticBezier, Arc
from ..plane import Matrix, Point
import re
import xml.sax

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
        self.transforms = [parse_transform(t) for t in transforms]
        self.data = data
        self.transform = Matrix.identity()
        for transform in self.transforms:
            self.transform *= transform

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

        return polygons

class Handler(xml.sax.ContentHandler):
    def __init__(self):
        self.stack = []
        self.paths = {}

    def startElement(self, tag, attributes):
        transform = None
        if 'transform' in attributes:
            transform = attributes['transform']
        if tag == 'g' and transform:
            self.stack.append(transform)
        if tag == 'path':
            transforms = list(self.stack)
            if transform: transforms.append(transform)
            self.paths[attributes['id']] = Path(transforms, attributes['d'])

    def endElement(self, tag):
        if tag == 'g':
            self.stack.pop()

def parse(source):
    parser = xml.sax.make_parser()
    svg = Handler()
    parser.setContentHandler(svg)
    parser.parse(source)
    return svg.paths
