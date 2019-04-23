import math
import unittest

from petrify.plane import tau, Line, LineSegment, Point, Polygon, Vector
from petrify.machine import Part, Pocket, StraightTip, Tab, LinearStepFeed
from petrify.machine.feed import batch_scanlines

inside = Polygon([Point(0, 0), Point(0, 3), Point(3, 3), Point(3, 0)])
outside = Polygon([Point(1, 1), Point(1, 2), Point(2, 2), Point(2, 1)])
pocket = Pocket([inside], [outside])

tip = StraightTip(0.5)
feed = LinearStepFeed(0.5, 0.1)

def y(y, pairs):
    pairs = [pairs] if isinstance(pairs, tuple) else pairs
    return [(Point(x1, y), Point(x2, y)) for x1, x2 in pairs]

class TestLinearStepFeed(unittest.TestCase):
    def test_scanlines(self):
        lines = feed.scanlines(pocket, tip)
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
        batches = batch_scanlines(feed.scanlines(pocket, tip))
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

    def test_toolpath(self):
        passes = feed.pocket_removal(pocket, tip)
        def fy(yl, line):
            fx = line[-1]
            # Account for the feed-up line segment.
            return [*y(yl, line), (Point(fx, yl), Point(fx, yl + 0.25))]

        paths = [[(l.p1, l.p2) for l in p.segments()] for p in passes]
        self.assertEqual(paths, [
            [
                *fy(0.75, (2.25, 2.75)),
                *fy(1.00, (2.75, 2.25)),
                *fy(1.25, (2.25, 2.75)),
                *fy(1.50, (2.75, 2.25)),
                *fy(1.75, (2.25, 2.75)),
                *fy(2.00, (2.75, 2.25)),
                *y(2.25, (2.25, 2.75)),
            ],
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

        part = Part(circle, [Tab(Line(Point(0, 0), Vector(0, 1)), 2)])
        self.assertEqual(len(feed.part(part, tip)), 2)

        for p in feed.part(part, tip):
            print('part')
            for l in p.segments(): print(l)
