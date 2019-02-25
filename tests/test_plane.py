import doctest, unittest

from petrify import plane
from petrify.plane import Polygon, Point

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
