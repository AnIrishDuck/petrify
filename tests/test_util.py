import unittest

from petrify import Point, Vector
from petrify.plane import LineSegment2
from petrify.util import locate_circle, frange

class RangeTests(unittest.TestCase):
    def test_frange_inclusive(self):
        self.assertEqual(
            list(frange(-1, -5, -1, inclusive=True)),
            [-1, -2, -3, -4, -5]
        )

    def test_basic_frange(self):
        self.assertEqual(
            list(frange(0, 2.99, 1.5, inclusive=True)),
            [0.0, 1.5, 2.99]
        )

    def test_frange_equals(self):
        self.assertEqual(list(frange(10, 10, 0.1, inclusive=True)), [10])

class CircleTests(unittest.TestCase):
    def test_angle(self):
        p = Point(1, 1)
        np = Vector(-1, 0)
        l = LineSegment2(Point(1, 0), Point(0, 0))

        self.assertEqual(locate_circle(p, np, l), (Point(0, 1), 1, 1))
        self.assertEqual(locate_circle(Point(1, 0), np, l), (Point(1, 0), 0, 0))
        self.assertEqual(locate_circle(Point(-5, 0), np, l), None)
        self.assertEqual(locate_circle(Point(5, 0), np, l), None)
