from ..plane import ComplexPolygon

class Part:
    def __init__(self, polygon, tabs, depth):
        assert depth > 0
        self.polygon = polygon
        if isinstance(self.polygon, ComplexPolygon):
            self.interior = polygon.interior
            self.exterior = polygon.exterior
        else:
            self.interior = []
            self.exterior = [polygon]
        self.tabs = tabs
        self.depth = depth

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
