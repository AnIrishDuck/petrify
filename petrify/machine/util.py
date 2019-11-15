import math

from ..util import locate_circle
from ..plane import Circle


class CutLine:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def interpolate(self, v):
        (sv, sp, sr), (ev, ep, er) = self.start, self.end
        progress = None if ev == sv else (v - sv) / (ev - sv)
        center = sp if progress is None else (progress * (ep - sp)) + sp
        r = sr if progress is None else (progress * (er - sr)) + sr
        return (center, r)

    @classmethod
    def from_lines(cls, a, b):
        def _close(p, r, l):
            return Circle(p, r).connect(l).v.magnitude_squared() < 0.001
        endpoints = [(dl, locate_circle(p, a.v.cross(), b)) for dl, p in ((0, a.p1), (1, a.p2))]
        endpoints = [(dl, s) for dl, s in endpoints if s is not None]
        endpoints = [(dl, (p, r, x)) for dl, (p, r, x) in endpoints if _close(p, r, b)]
        midpoints = [locate_circle(p, b.v.cross(), a) for p in (b.p1, b.p2)]
        midpoints = [s for s in midpoints if s is not None]
        midpoints = [(x, (p, r, x)) for p, r, x in midpoints if _close(p, r, a)]
        cuts = [cls.lead(a, b), *endpoints, *midpoints]
        ordered = [(x, p, r) for x, (p, r, _) in sorted(cuts, key=lambda v: (v[0], v[1][1]))]
        if len(ordered) < 2:
            return None
        else:
            return [CutLine(a, b) for a, b in zip(ordered, ordered[1:])]

    @classmethod
    def lead(cls, a, b):
        cs = [a.connect(p) for p in (b.p1, b.p2)]
        c = min(cs, key=lambda v: v.magnitude_squared())
        x = math.sqrt((c.p - a.p).magnitude_squared() / a.v.magnitude_squared())
        r = c.v.magnitude() / 2
        return (x, (c.p + (c.v / 2), r, x))

def clearance(segment, others):
    lines = [CutLine.from_lines(segment, other) for other in others]
    cuts = [l for _ls in lines if _ls is not None for l in _ls]
    cuts = [c for c in cuts if c is not None]

    ordered = sorted(cuts, key=lambda c: c.start[0])
    active = []
    path = []
    prior = None

    ix = 0

    points = sorted(set([p[0] for l in ordered for p in (l.start, l.end)]))
    for position in sorted(points):
        while ix < len(ordered) and ordered[ix].start[0] <= position:
            active.append(ordered[ix])
            ix += 1
        active = [line for line in active if position <= line.end[0]]

        places = [cut.interpolate(position) for cut in active]
        places = sorted(places, key=lambda pair: pair[1])
        path.append(places[0])

    return path
