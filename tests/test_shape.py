import doctest, unittest
from petrify import shape, Point

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(shape))
    return tests

class TestFillet(unittest.TestCase):
    def test_rounded_square(self):
        points = [Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)]
        actual = [point.snap(0.125)
                  for a, b, c in zip(points, [*points[1:], *points[:1]], [*points[2:], *points[:2]])
                  for point in list(shape.fillet(a, b, c, 0.25, segments=3))]

        expected = [
            Point(0.75, 0.0),
            Point(0.875, 0.125),
            Point(1.0, 0.25),
            Point(1.0, 0.75),
            Point(0.875, 0.875),
            Point(0.75, 1.0),
            Point(0.25, 1.0),
            Point(0.125, 0.875),
            Point(0.0, 0.75),
            Point(0.0, 0.25),
            Point(0.125, 0.125),
            Point(0.25, 0.0)
        ]

        self.assertEqual(actual, expected)
