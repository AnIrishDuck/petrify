import doctest, unittest

from petrify import plane
from petrify.plane import Polygon, Point, Ray, Vector

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(plane))
    return tests

class TestPolygon(unittest.TestCase):
    def test_inside(self):
        # taken from https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/fill-rule
        star = Polygon([
            Point(50, 0),
            Point(21, 90),
            Point(98, 35),
            Point(2, 35),
            Point(79, 90)
        ])

        self.assertTrue(star.contains(Point(50, 50)))

    def test_inwards(self):
        w = Polygon([
            Point(0, 0), Point(0, 2), Point(1, 2), Point(1, 1),
            Point(2, 1), Point(2, 2), Point(3, 2), Point(3, 1),
            Point(4, 1), Point(4, 2), Point(5, 2), Point(5, 0),
        ])

        down = Vector(0, -1)
        up = Vector(0, 1)
        left = Vector(-1, 0)
        right = Vector(1, 0)

        directions = [
            right, down, left, down,
            right, down, left, down,
            right, down, left,
            up
        ]

        for s, d in zip(w.segments(), directions):
            self.assertEqual(w.inwards(s), d)
