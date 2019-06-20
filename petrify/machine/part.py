from ..plane import ComplexPolygon

class Part:
    def __init__(self, polygon, tabs, depth, start=None):
        assert depth > 0
        self.polygon = polygon
        self.tabs = tabs
        self.depth = depth
        self.start = start or 0

    def __mul__(self, v):
        if not valid_scalar(v): return NotImplemented
        return Part(
            self.polygon * v,
            [t * v for t in self.tabs],
            self.depth * v,
            self.start * v
        )
    __rmul__ = __mul__

class Tab:
    def __init__(self, line, width):
        self.line = line
        self.width = width

        m = self.line.v.cross().normalized()
        Klass = self.line.__class__
        self.a = Klass(self.line.p + (m * width), self.line.v)
        self.b = Klass(self.line.p + (m * -width), self.line.v)

    def intersect(self, point):
        points = [l.intersect(point) for l in (self.a, self.b)]
        points = [p for p in points if p is not None]
        return points[0] if points else None

    def __mul__(self, v):
        if not valid_scalar(v): return NotImplemented
        return Tab(self.line * v, self.width * v)
    __rmul__ = __mul__
