"""
Utility methods for decomposition of polygons into simpler polygons.

"""
from petrify import space
from .plane import tau, LineSegment, Line, Ray
from . import geometry, plane
from .util import index_by
import heapq, itertools

# LineSegment stores a point and a vector. Thanks to floating point math,
# \exist p1, p2 in Point2 where p1 + (p2 - p1) != p2
# In other words, we need to store the exact endpoint instead of the offset for
# proper floating point comparison. See the double diamond test for an example.
class ExactSegment:
    def __init__(self, p1, p2):
        self.embedding = p1.embedding
        self.p1 = p1
        self.p2 = p2
        self.p = self.p1
        self.v = self.p2 - self.p1

    def intersect(self, other):
        return other._intersect_line2(self)

    def _u_in(self, u):
        return u >= 0.0 and u <= 1.0

    def _intersect_line2(self, other):
        return plane._intersect_line2_line2(self, other)

    def _connect_point2(self, other):
        return plane._connect_point2_line2(other, self)

    def _connect_point3(self, other):
        return space._connect_point3_line3(other, self)

    def flipped(self):
        return ExactSegment(self.p2, self.p1)

    def __repr__(self):
        return "{0!r} => {1!r}".format(self.p1, self.p2)

    def __hash__(self):
        return hash((self.p1, self.p2))

    def __eq__(self, other):
        return (self.p1, self.p2) == (other.p1, other.p2)

def exact_segments(p):
    pairs = zip(p.points, p.points[1:] + [p.points[0]])
    return [ExactSegment(p1, p2) for p1, p2 in pairs]

class Sliced(plane.Polygon):
    def __init__(self, points):
        super().__init__(points)
        self.heap = [(min(l.p1.y, l.p2.y), l) for l in self.segments()]
        self.heap.sort(key=lambda pair: pair[0])

    def departures(self, y):
        output = list(itertools.takewhile(lambda pair: pair[0] == y, self.heap))
        self.heap = self.heap[len(output):]
        return [pair[1] for pair in output if pair[1].p1.y != y or pair[1].p2.y != y]

    def segments(self):
        return exact_segments(self)

def grouper(n, iterable, fillvalue=None):
    args = [iter(iterable)] * n
    return itertools.zip_longest(fillvalue=fillvalue, *args)

def yl(segment, y):
    return segment.intersect(Line(plane.Point(0, y), plane.Vector(1, 0)))

def trapezoidal(polygons, min_area=None):
    """
    Trapezoidal decomposition of a list of :py:class:`petrify.plane.Polygon`
    objects forming a complex polygon that can be concave, consist of many
    disjoint rejoins, and contain holes.

    ..note ::
        Currently assumes that no edges cross or repeat.

    """
    polygons = [p.to_clockwise() for p in polygons]
    sliced = [Sliced(p.points) for p in polygons]
    order = {l: ix for p in sliced for ix, l in enumerate(p.segments())}

    levels = sorted(set(p.y for poly in sliced for p in poly.points))
    trapezoids = []
    active = []
    prior = None
    for level in levels:
        departures = [l for p in sliced for l in p.departures(level)]
        next_active = []
        for a in active:
            a = sorted(a, key=lambda l: order[l])

            a0 = yl(a[0], level)
            a1 = yl(a[1], level)
            trapezoids.append([
                yl(a[0], prior), a0,
                a1, yl(a[1], prior)
            ])

            if a[0].p1.y != level and a[0].p2.y != level:
                next_active.append((a0.x, a[0]))
            if a[1].p1.y != level and a[1].p2.y != level:
                next_active.append((a1.x, a[1]))

        for l in departures:
            next_active.append((yl(l, level).x, l))

        next_active.sort(key=lambda p: p[0])
        active = grouper(2, [a[1] for a in next_active])
        prior = level

    simplified = [plane.Polygon(t).simplify() for t in trapezoids
                  if min_area is None or trap_area(t) > min_area]
    return [p for p in simplified if p is not None and len(p.points) > 2]

def tri_area(a, b, c):
    return abs((a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y)) / 2)

def trap_area(polygon):
    a, b, c, d = polygon
    return tri_area(a, b, c) + tri_area(b, c, d)

def snap(l):
    return ExactSegment(l.p1.snap(geometry.quantum), l.p2.snap(geometry.quantum))

def fragment(segments, error=geometry.quantum):
    """
    Takes a list of line segments, and fragments any segment that is touched
    by the endpoint of another segment.

    """
    # TODO: this is incredibly inefficient (O(n^2)) without kd-trees
    fragments = []
    for ix, cutee in enumerate(segments):
        def non_overlapping(a, b):
            theta = a.v.angle(b.v)
            return theta != 0 and theta != tau / 2

        def not_close(a, b):
            return (a - b).magnitude_squared() > (error ** 2)

        before = itertools.islice(segments, ix)
        after = itertools.islice(segments, ix + 1, len(segments))
        connections = [
            (line, p.connect(cutee)) for line in (*before, *after)
            for p in [line.p1, line.p2]
            if not_close(p, cutee.p1) and not_close(p, cutee.p2)
            if non_overlapping(cutee, line)
        ]
        _intersects = [(x, l.p2) for x, l in connections if l.magnitude_squared() <= (error ** 2)]
        intersects = (v for _, v in _intersects)

        distance = lambda p: (cutee.p - p).magnitude_squared()
        parts = sorted(intersects, key=distance)
        points = [cutee.p1, *parts, cutee.p2]
        fragments.extend([ExactSegment(a, b) for a, b in zip(points, points[1:]) if not_close(a, b)])

    return fragments

def collate_collinear(polygon):
    embedding = polygon.embedding
    prior = embedding.LineSegment(polygon.points[-1], polygon.points[0])
    current = None
    points = []
    for a, b in zip(polygon.points, (*polygon.points[1:], polygon.points[0])):
        current = embedding.LineSegment(a, b)
        if abs(prior.v.angle(current.v)) > 0.0001:
            points.append(a)
        prior = current
    return embedding.Polygon(points)

def recreate_polygons(segments):
    """
    Takes a list of fragmented line segments and returns all polygons forming
    complete loops, ignoring all shared line segments.

    .. note::
        Currently assumes no polygons share points.

    """
    embedding = segments[0].embedding
    valid = set((snap(l) for l in segments))

    by_point = index_by(((p, l) for l in valid for p in (l.p1, l.p2)), lambda t: t[0])

    size = len(valid)

    polygons = []
    while valid:
        polygon = []
        l = next(iter(valid))
        valid.remove(l)
        p1, p2 = l.p1, l.p2
        first = p1
        polygon.append(p1)
        while p2:
            polygon.append(p2)
            ls = [l for _, l in by_point[p2]]
            l, = set(ls) - set([l])
            valid.remove(l)
            p1, p2 = l.p1, l.p2
            if p2 == first:
                p2 = None

        polygons.append(embedding.Polygon(polygon))
        assert(size != len(valid))
        size = len(valid)

    return polygons

def decouple(segments):
    fragments = fragment(segments)
    counts = {}
    for l in fragments:
        for k in (l, l.flipped()):
            k = snap(k)
            previous = counts.get(k, 0)
            counts[k] = previous + 1

    valid = [l for l in fragments if counts[snap(l)] == 1]
    return valid

def rebuild(simple):
    valid = [p.simplify() for p in simple if p.simplify() is not None]
    segments = [s for p in valid for s in exact_segments(p.simplify())]
    return [collate_collinear(p) for p in recreate_polygons(decouple(segments))]
