import unittest

from petrify.solid import Basis, Box, Point, Polygon, Vector
from petrify.shape import Rectangle
from petrify.plane import ComplexPolygon
from petrify.machine.slice import Sliced

class TestSliced(unittest.TestCase):
    def test_basic_case(self):
        a = Box(Point(0, 0, 0), Vector(1, 1, 1))
        b = Box(Point(0, 0, 2), Vector(1, 1, 1))
        cut = Box(Point(0.25, 0.25, 0.5), Vector(0.5, 0.5, 2))

        solid = (a + b + cut)
        r = Rectangle(Point(0, 0), Vector(5, 5))
        sliced = Sliced(solid, Basis.xy, r, 0.25, 2.75, 1.5)
        self.assertEqual(sliced.slices, [
            (0.25, [Polygon([Point(0.0, 0.0, 0.25), Point(0.0, 1.0, 0.25), Point(1.0, 1.0, 0.25), Point(1.0, 0.0, 0.25)])]),
            (1.75, [Polygon([Point(0.75, 0.25, 1.75), Point(0.25, 0.25, 1.75), Point(0.25, 0.75, 1.75), Point(0.75, 0.75, 1.75)])]),
            (2.75, [Polygon([Point(0.0, 0.0, 2.75), Point(0.0, 1.0, 2.75), Point(1.0, 1.0, 2.75), Point(1.0, 0.0, 2.75)])])
        ])
