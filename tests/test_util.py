import unittest

from petrify import Point, Vector
from petrify.plane import LineSegment2
from petrify.util import locate_circle

class CircleTests(unittest.TestCase):
    def test_angle(self):
        p = Point(1, 1)
        np = Vector(-1, 0)
        l = LineSegment2(Point(1, 0), Point(0, 0))

        self.assertEqual(locate_circle(p, np, l), [Point(0, 1), 1, 1])
        self.assertEqual(locate_circle(Point(1, 0), np, l), [Point(1, 0), 0, 0])
        self.assertEqual(locate_circle(Point(-5, 0), np, l), None)
        self.assertEqual(locate_circle(Point(5, 0), np, l), None)
