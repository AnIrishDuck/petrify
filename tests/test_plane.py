import doctest, unittest

from petrify import plane
from petrify.plane import ComplexPolygon, Polygon, Point, Ray, Vector, line, point

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(plane))
    tests.addTests(doctest.DocTestSuite(line))
    tests.addTests(doctest.DocTestSuite(point))
    return tests

class TestVector(unittest.TestCase):
    def test_angle(self):
        a = Vector(0.11176897466954505, 0.056949137058031396)
        b = Vector(0.016835599543175706, 0.008578166424744738)
        a.angle(b)

    def test_builtins(self):
        self.assertTrue(Vector(1, 1) == [1, 1])
        self.assertTrue(Vector(1, 1) == Vector(1, 1))
        self.assertEqual(Vector(1, 1) + [1, 1], Vector(2, 2))
        self.assertEqual(Vector(1, 1) - [1, 1], Vector(0, 0))

        with self.assertRaises(TypeError):
            self.assertEqual(Vector(1, 1) + [1], Vector(2, 2))
        with self.assertRaises(TypeError):
            self.assertEqual(Vector(1, 1) - [1], Vector(2, 2))
        with self.assertRaises(TypeError):
            self.assertEqual(Vector(1, 1) * [1], Vector(2, 2))
        with self.assertRaises(TypeError):
            self.assertEqual(Vector(1, 1) / [1], Vector(2, 2))

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

        self.assertEqual(list(square.offset(-0.1).points), [
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
            Point(10 + 3, 5),
            Point(10, 5),
            Point(10 + (3 / 2), 5 + (4 / 2))
        ])

    def test_offset_square(self):
        square = Polygon([
            Point(0, 0),
            Point(3, 0),
            Point(3, 3),
            Point(0, 3)
        ])

        parts = square.offset(-0.25)
        self.assertEqual(
            set(c for poly in parts.polygons for p in poly.points for c in (p.x, p.y)),
            set([0.25, 2.75])
        )

    def test_offset_split_notch(self):
        notch = Polygon([
            Point(0, 0),
            Point(6, 0),
            Point(6, 5),
            Point(3, 1),
            Point(0, 5)
        ])

        parts = notch.offset(-(0.375 + 0.1))

        self.assertEqual(len(parts.polygons), 2)

    def test_offset_foot_double_merge(self):
        foot = Polygon([
            Point(0, 0),
            Point(10, 0),
            Point(10, 1),
            Point(10, 10),
            Point(1, 10),
            Point(1, 2),
            Point(0, 1)
        ])
        rect = foot.offset(-2)
        self.assertEqual(len(rect.polygons[0].points), 4)

    def test_offset_merge(self):
        notch = Polygon([
            Point(0, 0),
            Point(7, 0),
            Point(4, 4),
            Point(3, 4)
        ])

        parts = notch.offset(-(1.0 + 0.1))

        self.assertEqual(len(parts.polygons), 1)
        self.assertEqual(len(parts.polygons[0].points), 3)

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

        self.assertEqual(list(square.offset(0.1).points), [
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

        moved = polygon * 2

        self.assertEqual(moved.interior, [
            Polygon([Point(1, 1), Point(1, 2), Point(2, 2), Point(2, 1)]) * 2
        ])

        self.assertEqual(moved.exterior, [
            Polygon([Point(0, 0), Point(0, 3), Point(3, 3), Point(3, 0)]) * 2
        ])

        moved = polygon / 2

        self.assertEqual(moved.interior, [
            Polygon([Point(1, 1), Point(1, 2), Point(2, 2), Point(2, 1)]) / 2
        ])

        self.assertEqual(moved.exterior, [
            Polygon([Point(0, 0), Point(0, 3), Point(3, 3), Point(3, 0)]) / 2
        ])

    def test_complex_offset_cleanup(self):
        polygon = ComplexPolygon([
            Polygon([Point(0, 0), Point(0, 100), Point(100, 100), Point(100, 0)]),
            Polygon([Point(1, -1), Point(1, -2), Point(2, -2), Point(2, -1)])
        ])

        self.assertEqual(len(polygon.offset(-2).exterior), 1)
