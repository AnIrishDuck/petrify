"""
Utility methods for decomposition of polygons into simpler polygons.

"""
from .plane import Point, Polygon, LineSegment, Line, Ray, Vector
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

    return [t for t in trapezoids if trap_area(t) > min_area]

def tri_area(a, b, c):
    return abs((a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y)) / 2)

def trap_area(polygon):
    a, b, c, d = polygon
    return tri_area(a, b, c) + tri_area(b, c, d)
