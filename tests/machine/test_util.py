import unittest

from petrify import Point
from petrify.plane import LineSegment2
from petrify.machine.util import frange, CutLine

class TestUtil(unittest.TestCase):
    def test_frange_inclusive(self):
        self.assertEqual(
            list(frange(-1, -5, -1, inclusive=True)),
            [-1, -2, -3, -4, -5]
        )


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
