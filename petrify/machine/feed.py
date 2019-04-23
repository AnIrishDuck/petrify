import math

from ..plane import Line, LineSegment, Point, Vector
from ..decompose import grouper

def frange(a, b, step, inclusive=False):
    count = math.floor((b - a) / step) if a != b else 1
    for ix in range(0, count):
        v = a + (ix * step)
        if v != b: yield v

    if inclusive: yield b

class PlanarToolpath:
    """
    Planar toolpaths are continuous movements of the tool that require no
    clearance.

    """
    def __init__(self, start):
        self.path = [start]

    def move_to(self, p):
        self.path.append(p)

    def segments(self):
        return [LineSegment(a, b) for a, b in zip(self.path, self.path[1:])]

    @property
    def current(self):
        return self.path[-1]

class ScanlineToolpath(PlanarToolpath):
    """ A toolpath formed from clustered scanlines. """
    def __init__(self, scanlines):
        super().__init__(scanlines[0][0])
        self.move_to(scanlines[0][1])
        for l in scanlines[1:]:
            # When extended past the start / endpoint of the next scanline,
            # move back to where a move down won't cut stock.
            if self.current.x < l[0].x:
                self.move_over(l[0])
            if self.current.x > l[1].x:
                self.move_over(l[1])

            self.move_to(Point(self.current.x, l[0].y))

            current_distance = lambda p: (self.current - p).magnitude_squared()
            near, far = sorted((p for p in l), key=current_distance)

            if near != self.current:
                self.move_to(near)
            self.move_to(far) # whereveeeer you areeeee...

    def move_over(self, endpoint):
        self.move_to(Point(endpoint.x, self.current.y))

def batch_scanlines(scanlines):
    """
    Greedy algorithm batching successive scanlines against the first prior
    scanline shape from above that overlaps it.

    """
    final_shapes = []
    current_shapes = []
    for level_lines in scanlines:
        next_shapes = []
        for line in level_lines:
            matched = False
            for ix, shape in enumerate(current_shapes):
                ax0, ax1 = shape[-1][0].x, shape[-1][1].x
                bx0, bx1 = line[0].x, line[1].x
                if (bx0 >= ax0 and bx0 <= ax1) or (bx1 >= ax0 and bx1 <= ax1):
                    shape.append(line)
                    next_shapes.append(shape)
                    matched = True
                    break

            if matched:
                current_shapes.pop(ix)
            else:
                next_shapes.append([line])

        final_shapes.extend(current_shapes)
        current_shapes = next_shapes

    return [*final_shapes, *current_shapes]

def bounding_lines(polygons, offset):
    return (
        l for p in polygons for l in p.offset(offset).segments()
        if l.v.y != 0
    )

class LinearStepFeed:
    """
    A feed strategy using linear stepover along y-axis scanlines to remove the
    desired material.

    """

    def __init__(self, stepover, dz):
        assert(stepover > 0 and stepover <= 1)
        self.stepover = stepover
        self.dz = dz

    def part(self, part, tip):
        outline = part.outline.offset(tip.radius)

        active = None
        paths = [PlanarToolpath(outline.points[0])]
        for line in outline.segments():
            for tab in part.tabs:
                i = tab.intersect(line)
                if i is not None:
                    if active is None:
                        active = tab
                        paths[-1].move_to(i)
                    else:
                        active = None
                        paths.append(PlanarToolpath(i))

            if active is None:
                paths[-1].move_to(line.p2)

        return paths

    def pocket_removal(self, pocket, tip):
        lines = self.scanlines(pocket, tip)
        return [ScanlineToolpath(b) for b in batch_scanlines(lines)]

    def scanlines(self, pocket, tip):
        inside = bounding_lines(pocket.inside, -tip.radius)
        outside = bounding_lines(pocket.outside, tip.radius)
        bounds = [*inside, *outside]

        start = min(y for l in bounds for y in (l.p1.y, l.p2.y))
        end = max(y for l in bounds for y in (l.p1.y, l.p2.y))

        # Horrendously inefficient O(scanlines * polygonlines) algorithm.
        # TODO: remove the quadratic relationship by using the sweep approach
        # from trapezoidal decomposition.
        scanlines = []
        stepover = self.stepover * tip.diameter
        for y in (*frange(start, end, stepover), end):
            scan = Line(Point(0, y), Vector(1, 0))
            intersects = [scan.intersect(l) for l in bounds]
            xs = sorted(i.x for i in intersects if i is not None)
            points = (Point(x, y) for x in xs)
            scanlines.append([(a, b) for a, b in grouper(2, points)])

        return scanlines

    def batch_scanlines(self, shapes):
        """
        inside = (
            (min(l.p1.y, l.p2.y), (tip.radius, l))
            for p in pocket.inside for l in p.segments()
            if l.v.y != 0
        )
        outside = (
            (min(l.p1.y, l.p2.y), (-tip.radius, l))
            for p in pocket.outside for l in p.segments()
            if l.v.y != 0
        )

        heap = inside + outside
        heap.sort(key=lambda pair: pair[0])

        def departures(y):
            output = list(itertools.takewhile(lambda pair: pair[0] == y, heap))
            heap = heap[len(output):]
            return [pair[1] for pair in output if pair[1].p1.y != y or pair[1].p2.y != y]

        levels = sorted(
            set(p.y for polygon in (*inside, *outside) for p in polygon.points)
        )

        active = departures(levels.pop(0))
        stepover = self.stepover * tip.diameter
        for y in frange(start, end, stepover):
            while levels[0] <= y:
                ly = levels.pop(0)
                continuing = (l for l in active if max(l[1].p1.y, l[1].p2.y) > y)
                active = [*continuing, *departures(ly)]

            scan = Line(Point(0, y), Vector(1, 0))
            points = [scan.intersect(l).x + o for o, l in active]

        # Find topmost point
        # Generate scanlines
        # Batch areas
        # Return feedlines
        """
