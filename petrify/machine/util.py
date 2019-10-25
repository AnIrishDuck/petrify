import math

from ..util import locate_circle
from ..plane import Circle

def frange(a, b, step, inclusive=False):
    count = math.floor((b - a) / step) if a != b else 1
    for ix in range(0, count):
        v = a + (ix * step)
        if v != b: yield v

    if inclusive: yield b

class CutLine:
    def __init__(self, start, end):
        self.start = start
        self.end = end

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
        ordered = [(x, p, r) for x, (p, r, _) in sorted(endpoints + midpoints, key=lambda v: (v[0], v[1][1]))]
        return None if len(ordered) < 2 else CutLine(ordered[0], ordered[-1])
