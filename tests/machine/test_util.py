import unittest

from petrify import Point, Polygon
from petrify.plane import LineSegment2
from petrify.machine.util import clearance, CutLine

class TestCutLine(unittest.TestCase):
    def test_parallel_lines(self):
        a = LineSegment2(Point(1, 0), Point(0, 0))
        b = LineSegment2(Point(-2, 1), Point(2, 1))

        line = CutLine.from_lines(a, b)
        self.assertEqual(line.start, (0, Point(1, 0.5), 0.5))
        self.assertEqual(line.end, (1, Point(0, 0.5), 0.5))

        reversed = CutLine.from_lines(b, a)
        self.assertEqual(reversed.start, (0.5, Point(0, 0.5), 0.5))
        self.assertEqual(reversed.end, (0.75, Point(1, 0.5), 0.5))

class TestClearance(unittest.TestCase):
    def test_indent(self):
        segments = Polygon([
            Point(0, 0),
            Point(0, 6),
            Point(2, 6),
            Point(2, 4),
            Point(1, 4),
            Point(1, 2),
            Point(2, 2),
            Point(2, 0)
        ]).segments()

        path = clearance(segments[0], segments[1:])
        expected = [
            (Point(0.0, 0.0), 0.0),
            (Point(1.0, 1.0), 1.0),
            (Point(0.5, 2.0), 0.5),
            (Point(0.5, 4.0), 0.5),
            (Point(1.0, 5.0), 1.0),
            (Point(0.0, 6.0), 0.0)
        ]
        self.assertEqual([(c.snap(0.25), round(r, 1)) for c, r in path], expected)
