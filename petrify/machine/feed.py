import math

from .motion import PlanarToolpath, CutSteps
from .util import frange

from ..plane import Line, LineSegment, Point, Vector
from ..decompose import grouper

from .. import units

def bounding_lines(polygons, offset):
    return (
        l for p in polygons for l in p.offset(offset).segments()
        if l.v.y != 0
    )

class Speed:
    """
    Configures machining `xy` and `z` feed rates:

    >>> from petrify import u
    >>> speed = Speed(900 * u.mm / u.minute, 300 * u.mm / u.minute)

    """
    def __init__(self, xy, z):
        self.xy = units.assert_speedy(xy)
        self.z = units.assert_speedy(z)

class Steps:
    def __init__(self, top, bottom, step):
        self.top = top
        self.bottom = bottom
        self.step = step

    def __iter__(self):
        return frange(self.top, self.bottom, self.step, inclusive=True)

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
            if line[1] is None: continue
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

class LinearStepFeed:
    """
    A feed strategy using linear stepover along y-axis scanlines to remove the
    desired material.

    """

    def __init__(self, stepover, dz):
        assert(stepover > 0 and stepover <= 1)
        assert(dz > 0)
        self.stepover = stepover
        self.dz = dz

    def step(self, configuration, toolpaths, shape):
        start = shape.start or self.dz
        assert start > 0
        steps = Steps(-start, -shape.depth, -self.dz)
        return CutSteps(toolpaths, steps, configuration)

    def pocket(self, configuration, pocket):
        lines = self.scanlines(configuration, pocket)
        paths = [ScanlineToolpath(b) for b in batch_scanlines(lines)]
        paths = sorted(paths, key=lambda p: p.path[0].x)
        return self.step(configuration, paths, pocket)

    def scanlines(self, configuration, pocket):
        tool = configuration.tool
        off = pocket.polygon.offset(-tool.radius)
        bounds = [
            l for l in off.segments()
            if l.v.y != 0
        ]

        start = min(y for l in bounds for y in (l.p1.y, l.p2.y))
        end = max(y for l in bounds for y in (l.p1.y, l.p2.y))

        # Horrendously inefficient O(scanlines * polygonlines) algorithm.
        # TODO: remove the quadratic relationship by using the sweep approach
        # from trapezoidal decomposition.
        scanlines = []
        stepover = self.stepover * tool.diameter
        for y in (*frange(start, end, stepover), end):
            scan = Line(Point(0, y), Vector(1, 0))
            intersects = [scan.intersect(l) for l in bounds]
            xs = sorted(i.x for i in intersects if i is not None)
            points = (Point(x, y) for x in xs)
            scanlines.append([(a, b) for a, b in grouper(2, points)])

        return scanlines

    def part(self, configuration, part):
        tool = configuration.tool
        off = part.polygon.offset(tool.radius)

        all_paths =  []
        active = None
        for outline in off.polygons():
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

            all_paths.extend(paths)

        return self.step(configuration, all_paths, part)

    def engrave(self, configuration, engrave):
        def path(polygon):
            p = PlanarToolpath(None)
            p.path = [*polygon.points, polygon.points[0]]
            return p

        toolpaths = [path(polygon) for polygon in engrave.polygon.polygons()]
        toolpaths = sorted(toolpaths, key=lambda p: p.path[0].x)

        steps = Steps(-engrave.depth, -engrave.depth, -self.dz)
        return CutSteps(toolpaths, steps, configuration)
