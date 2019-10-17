# Geometry
# Much maths thanks to Paul Bourke, http://astronomy.swin.edu.au/~pbourke
# ---------------------------------------------------------------------------
import math
import numbers

quantum = 0.000001
tau = math.pi * 2

def valid_scalar(v):
    """
    Checks if `v` is a valid scalar value for the purposes of this library:

    >>> valid_scalar(1)
    True
    >>> valid_scalar(1.0)
    True
    >>> valid_scalar('abc')
    False

    """
    return isinstance(v, numbers.Number)

class AbstractPolygon:
    def __mul__(self, m):
        if isinstance(m, self.embedding.Vector):
            m = self.embedding.Matrix.scale(*m)
        return self.embedding.Polygon([p * m for p in self.points])

    def __add__(self, v):
        m = self.embedding.Matrix.translate(*v)
        return self.embedding.Polygon([p * m for p in self.points])

    def __eq__(self, other):
        return all(a == b for a, b in zip(self.points, other.points))

    def __len__(self):
        return len(self.points)

    def segments(self):
        pairs = zip(self.points, self.points[1:] + [self.points[0]])
        return [self.embedding.LineSegment(a, b) for a, b in pairs]

    def polygons(self):
        return [self]

    def simplify(self, tolerance):
        prior = self.points[-1].snap(tolerance)
        points = []
        for point in self.points:
            snapped = point.snap(tolerance)
            if snapped != prior:
                points.append(point)
                prior = snapped
        return self.embedding.Polygon(points) if len(points) > 2 else None

class Geometry:
    def _connect_unimplemented(self, other):
        raise AttributeError('Cannot connect %s to %s' %
                             (self.__class__, other.__class__))

    def _intersect_unimplemented(self, other):
        raise AttributeError('Cannot intersect %s and %s' %
                             (self.__class__, other.__class__))

    _intersect_point2 = _intersect_unimplemented
    _intersect_line2 = _intersect_unimplemented
    _intersect_circle = _intersect_unimplemented
    _connect_point2 = _connect_unimplemented
    _connect_line2 = _connect_unimplemented
    _connect_circle = _connect_unimplemented

    _intersect_point3 = _intersect_unimplemented
    _intersect_line3 = _intersect_unimplemented
    _intersect_sphere = _intersect_unimplemented
    _intersect_plane = _intersect_unimplemented
    _connect_point3 = _connect_unimplemented
    _connect_line3 = _connect_unimplemented
    _connect_sphere = _connect_unimplemented
    _connect_plane = _connect_unimplemented

    def intersect(self, other):
        raise NotImplementedError

    def connect(self, other):
        raise NotImplementedError

    def distance(self, other):
        c = self.connect(other)
        if c:
            return c.length
        return 0.0
