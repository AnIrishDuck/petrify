import doctest, unittest

from petrify import plane
from petrify.plane import ComplexPolygon, Polygon, Point, Ray, Vector

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(plane))
    return tests

class TestPolygon(unittest.TestCase):
    def test_star_contain(self):
        # taken from https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/fill-rule
        # we use the evenodd fill-rule so we don't have to calculate crossing
        # orientation.
        star = Polygon([
            Point(50, 0),
            Point(21, 90),
            Point(98, 35),
            Point(2, 35),
            Point(79, 90)
        ])

        self.assertFalse(star.contains(Point(50, 50)))

    def test_contain_through_point(self):
        # when we cross through a vertex, it still only should count as one
        # boundary crossing for evenodd purposes.
        shape = Polygon([
            Point(-1, 0),
            Point(0, 1),
            Point(1, 0),
            Point(0, -1)
        ])

        self.assertTrue(shape.contains(Point(0, 0)))
        self.assertTrue(shape.contains(Point(-0.5, 0)))
        self.assertTrue(shape.contains(Point(0, -0.5)))
        self.assertTrue(shape.contains(Point(0, 0.5)))
        self.assertTrue(shape.contains(Point(0.5, 0)))

        self.assertFalse(shape.contains(Point(2, 0)))
        self.assertFalse(shape.contains(Point(0, 2)))
        self.assertFalse(shape.contains(Point(0, -2)))
        self.assertFalse(shape.contains(Point(-2, 0)))

    def test_contain_through_lines(self):
        shape = Polygon([
            Point(0, 0),
            Point(0, 1),
            Point(1, 1),
            Point(1, 0)
        ])

        self.assertFalse(shape.contains(Point(-1, 0)))
        self.assertFalse(shape.contains(Point(0, -1)))
        self.assertFalse(shape.contains(Point(2, 0)))
        self.assertFalse(shape.contains(Point(0, 2)))

    def test_point_on_shape(self):
        shape = Polygon([
            Point(0, 0),
            Point(0, 1),
            Point(1, 1),
            Point(1, 0)
        ])

        self.assertTrue(shape.contains(Point(0.5, 0)))
        self.assertTrue(shape.contains(Point(0, 0.5)))
        self.assertTrue(shape.contains(Point(1, 0.5)))
        self.assertTrue(shape.contains(Point(0.5, 1)))

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

    def test_inset(self):
        square = Polygon([
            Point(0, 0),
            Point(0, 1),
            Point(1, 1),
            Point(1, 0)
        ])

        self.assertEqual(square.offset(-0.1).points, [
            Point(0.1, 0.1),
            Point(0.1, 0.9),
            Point(0.9, 0.9),
            Point(0.9, 0.1)
        ])

    def test_inset_local_merge(self):
        # the magic of 3-4-5 triangles...
        trapezoid = Polygon([
            Point(0, 0),
            Point(9, 12),
            Point(9 + 5, 12),
            Point(9 + 5 + 9, 0)
        ])

        self.assertEqual([p.round(4) for p in trapezoid.offset(-5).points], [
            Point(10, 5),
            Point(10 + (3 / 2), 5 + (4 / 2)),
            Point(10 + 3, 5)
        ])

    @unittest.skip
    def test_inset_split(self):
        dumbbell = Polygon([
            Point(0, 0),
            Point(0, 3),
            Point(1, 3),
            Point(1, 4),
            Point(0, 4),
            Point(0, 7),
            Point(3, 7),
            Point(3, 4),
            Point(2, 4),
            Point(2, 3),
            Point(3, 3),
            Point(3, 0)
        ])

        self.assertEqual(dumbbell.inset(2), [
            Polygon([
                Point(1, 5),
                Point(1, 6),
                Point(2, 6),
                Point(2, 5)
            ]),
            Polygon([
                Point(1, 1),
                Point(1, 2),
                Point(2, 2),
                Point(2, 1)
            ])
        ])

    def test_outset(self):
        square = Polygon([
            Point(0, 0),
            Point(0, 1),
            Point(1, 1),
            Point(1, 0)
        ])

        self.assertEqual(square.offset(0.1).points, [
            Point(-0.1, -0.1),
            Point(-0.1, 1.1),
            Point(1.1, 1.1),
            Point(1.1, -0.1)
        ])

class TestComplexPolygon(unittest.TestCase):
    def test_complex_add(self):
        polygon = ComplexPolygon([
            Polygon([Point(0, 0), Point(0, 3), Point(3, 3), Point(3, 0)]),
            Polygon([Point(1, 1), Point(1, 2), Point(2, 2), Point(2, 1)])
        ])

        moved = polygon + Vector(20, 10)

        self.assertEqual(moved.interior, [
            Polygon([Point(1, 1), Point(1, 2), Point(2, 2), Point(2, 1)]) + Vector(20, 10)
        ])

        self.assertEqual(moved.exterior, [
            Polygon([Point(0, 0), Point(0, 3), Point(3, 3), Point(3, 0)]) + Vector(20, 10)
        ])

    def test_complex_multiply(self):
        polygon = ComplexPolygon([
            Polygon([Point(0, 0), Point(0, 3), Point(3, 3), Point(3, 0)]),
            Polygon([Point(1, 1), Point(1, 2), Point(2, 2), Point(2, 1)])
        ])

        moved = polygon * Vector(20, 10)

        self.assertEqual(moved.interior, [
            Polygon([Point(1, 1), Point(1, 2), Point(2, 2), Point(2, 1)]) * Vector(20, 10)
        ])

        self.assertEqual(moved.exterior, [
            Polygon([Point(0, 0), Point(0, 3), Point(3, 3), Point(3, 0)]) * Vector(20, 10)
        ])
