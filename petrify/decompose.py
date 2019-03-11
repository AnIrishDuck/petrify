"""
Utility methods for decomposition of polygons into simpler polygons.

"""
from .plane import tau, Point, Polygon, LineSegment, Line, Ray, Vector
import heapq, itertools

class Sliced(Polygon):
    def __init__(self, points):
        super().__init__(points)
        self.heap = [(min(l.p1.y, l.p2.y), l) for l in self.segments()]
        self.heap.sort(key=lambda pair: pair[0])

    def departures(self, y):
        output = list(itertools.takewhile(lambda pair: pair[0] == y, self.heap))
        self.heap = self.heap[len(output):]
        return [pair[1] for pair in output if pair[1].p1.y != y or pair[1].p2.y != y]

def grouper(n, iterable, fillvalue=None):
    args = [iter(iterable)] * n
    return itertools.zip_longest(fillvalue=fillvalue, *args)

def yl(segment, y):
    return segment.intersect(Line(Point(0, y), Vector(1, 0)))

def trapezoidal(points, min_area=0.0001):
    """
    Trapezoidal decomposition of a linear cycle of :py:class:`petrify.plane.Point`
    objects forming a potentially concave polygon.

    ..note ::
        Currently assumes that no edges cross or repeat.

    """
    p = Sliced(points)
    order = {l: ix for ix, l in enumerate(p.segments())}

    levels = sorted(set(p.y for p in points))
    trapezoids = []
    active = []
    prior = None
    for level in levels:
        departures = p.departures(level)
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

    return [Polygon(t) for t in trapezoids if trap_area(t) > min_area]

def tri_area(a, b, c):
    return abs((a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y)) / 2)

def trap_area(polygon):
    a, b, c, d = polygon
    return tri_area(a, b, c) + tri_area(b, c, d)

def fragment(segments, error=0.0001):
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

        before = itertools.islice(segments, ix)
        after = itertools.islice(segments, ix + 1, len(segments))
        connections = [
            (line, p.connect(cutee)) for line in (*before, *after)
            for p in [line.p1, line.p2]
            if p != cutee.p1 and p != cutee.p2
            if non_overlapping(cutee, line)
        ]
        _intersects = [(x, l.p2) for x, l in connections if l.magnitude_squared() <= (error ** 2)]
        intersects = (v for _, v in _intersects)

        distance = lambda p: (cutee.p - p).magnitude_squared()
        parts = sorted(intersects, key=distance)
        points = [cutee.p1, *parts, cutee.p2]
        fragments.extend([LineSegment(a, b) for a, b in zip(points, points[1:])])

    return fragments

def index_by(it, f):
    # why this isn't a stdlib function like in every other sane language escapes
    # me...
    d = {}
    for i in it:
        k = f(i)
        previous = d.get(k, [])
        previous.append(i)
        d[k] = previous
    return d

def recreate_polygons(segments):
    """
    Takes a list of fragmented line segments and returns all polygons forming
    complete loops, ignoring all shared line segments.

    .. note::
        Currently assumes no polygons share points.

    """
    valid = set(segments)
    backwards = set(LineSegment(l.p2, l.p1) for l in segments)

    for segment in segments:
        if segment in backwards:
            valid.remove(segment)

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

        polygons.append(Polygon(polygon))
        assert(size != len(valid))
        size = len(valid)

    return polygons
