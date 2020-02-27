import math
import unittest

from petrify import u
from petrify.plane import tau, ComplexPolygon, Line, LineSegment, Point, Polygon, Vector
from petrify.machine import (
    Engrave,
    Part,
    Pocket,
    StraightTip,
    Tab,
    LinearStepFeed,
    Machine,
    Format
)
from petrify.machine.feed import batch_scanlines, Speed
from petrify.shape import Circle

gspeed = u.mm / u.minute
mpcnc = Machine(clearance=2.0 * u.mm, format=Format(u.mm, v = u.mm / u.minute))
speeds = Speed(xy=900 * gspeed, z=200 * gspeed)
tool = StraightTip(1, 0.5) * u.mm
feed = LinearStepFeed(0.5, 1.0 * u.mm / u.layer)
config = mpcnc.configure(feed, speeds, tool)

def y(y, pairs):
    pairs = [pairs] if isinstance(pairs, tuple) else pairs
    return [(Point(x1, y), Point(x2, y)) for x1, x2 in pairs]

class TestLinearStepFeed(unittest.TestCase):
    def pocket(self):
        polygon = ComplexPolygon([
            Polygon([Point(0, 0), Point(0, 3), Point(3, 3), Point(3, 0)]),
            Polygon([Point(1, 1), Point(1, 2), Point(2, 2), Point(2, 1)])
        ])
        return Pocket(polygon, 1.0)

    def test_scanlines(self):
        lines = feed.scanlines(config, self.pocket())
        self.assertEqual(lines, [
            y(0.25, [(0.25, 2.75)]),
            y(0.50, [(0.25, 2.75)]),
            y(0.75, [(0.25, 0.75), (2.25, 2.75)]),
            y(1.00, [(0.25, 0.75), (2.25, 2.75)]),
            y(1.25, [(0.25, 0.75), (2.25, 2.75)]),
            y(1.50, [(0.25, 0.75), (2.25, 2.75)]),
            y(1.75, [(0.25, 0.75), (2.25, 2.75)]),
            y(2.00, [(0.25, 0.75), (2.25, 2.75)]),
            y(2.25, [(0.25, 0.75), (2.25, 2.75)]),
            y(2.50, [(0.25, 2.75)]),
            y(2.75, [(0.25, 2.75)]),
        ])

    def test_batching(self):
        batches = batch_scanlines(feed.scanlines(config, self.pocket()))
        self.assertEqual(sorted(batches, key=lambda b: len(b)), [
            [
                *y(0.75, (2.25, 2.75)),
                *y(1.00, (2.25, 2.75)),
                *y(1.25, (2.25, 2.75)),
                *y(1.50, (2.25, 2.75)),
                *y(1.75, (2.25, 2.75)),
                *y(2.00, (2.25, 2.75)),
                *y(2.25, (2.25, 2.75)),
            ],
            [
                *y(0.25, (0.25, 2.75)),
                *y(0.50, (0.25, 2.75)),
                *y(0.75, (0.25, 0.75)),
                *y(1.00, (0.25, 0.75)),
                *y(1.25, (0.25, 0.75)),
                *y(1.50, (0.25, 0.75)),
                *y(1.75, (0.25, 0.75)),
                *y(2.00, (0.25, 0.75)),
                *y(2.25, (0.25, 0.75)),
                *y(2.50, (0.25, 2.75)),
                *y(2.75, (0.25, 2.75)),
            ]
        ])

    def test_batching_from_bottom_overlap(self):
        polygon = Circle(Point(0, 0), 2.0)
        pocket = Pocket(polygon, 1.0)
        batches = batch_scanlines(feed.scanlines(config, pocket))
        self.assertEqual(len(batches), 1)

    def test_toolpath(self):
        passes = feed.pocket(config, self.pocket()).passes
        def fy(yl, line):
            fx = line[-1]
            # Account for the feed-up line segment.
            return [*y(yl, line), (Point(fx, yl), Point(fx, yl + 0.25))]

        paths = [[(l.p1, l.p2) for l in p.segments()] for p in passes]
        self.assertEqual(paths, [
            [
                *fy(0.25, (0.25, 2.75)),
                *fy(0.50, (2.75, 0.25)),
                *fy(0.75, (0.25, 0.75)),
                *fy(1.00, (0.75, 0.25)),
                *fy(1.25, (0.25, 0.75)),
                *fy(1.50, (0.75, 0.25)),
                *fy(1.75, (0.25, 0.75)),
                *fy(2.00, (0.75, 0.25)),
                *fy(2.25, (0.25, 0.75)),
                # need to move over after feeding up halfway into a line
                (Point(0.75, 2.50), Point(0.25, 2.50)),
                *fy(2.50, (0.25, 2.75)),
                *y(2.75, (2.75, 0.25)),
            ],
            [
                *fy(0.75, (2.25, 2.75)),
                *fy(1.00, (2.75, 2.25)),
                *fy(1.25, (2.25, 2.75)),
                *fy(1.50, (2.75, 2.25)),
                *fy(1.75, (2.25, 2.75)),
                *fy(2.00, (2.75, 2.25)),
                *y(2.25, (2.25, 2.75)),
            ]
        ])

    def test_part(self):
        r = 10
        n = 6
        angles = [tau * i / n for i in range(n)]
        circle = Polygon([
            Point(math.cos(theta) * r, math.sin(theta) * r)
            for theta in angles
        ])

        part = Part(circle, [Tab(Line(Point(0, 0), Vector(0, 1)), 2)], 1.0)
        passes = feed.part(config, part).passes
        self.assertEqual(len(passes), 2)

    def test_unworkable_pocket_removal(self):
        polygon = ComplexPolygon([
            Polygon([Point(0, 0), Point(0, 100), Point(100, 100), Point(100, 0)]),
            Polygon([Point(1, -1), Point(1, -1.25), Point(1.25, -1.25), Point(1.25, -1)])
        ])
        pocket = Pocket(polygon, 1.0)

        passes = feed.pocket(config, pocket).passes
        self.assertEqual(len(passes), 1)

    def test_unworkable_part_removal(self):
        polygon = ComplexPolygon([
            Polygon([Point(0, 0), Point(0, 100), Point(100, 100), Point(100, 0)]),
            Polygon([Point(1, 1), Point(1, 1.25), Point(1.25, 1.25), Point(1.25, 1)])
        ])
        pocket = Part(polygon, [], 1.0)

        passes = feed.part(config, pocket).passes
        self.assertEqual(len(passes), 1)

    def test_engrave(self):
        polygon = ComplexPolygon([
            Polygon([Point(0, 0), Point(0, 100), Point(100, 100), Point(100, 0)]),
            Polygon([Point(1, 1), Point(1, 1.25), Point(1.25, 1.25), Point(1.25, 1)])
        ])

        engrave = Engrave(polygon, 0.5)
        passes = feed.engrave(config, engrave).passes
        self.assertEqual(len(passes[0].path), 5)
