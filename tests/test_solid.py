import doctest, unittest
from petrify import plane, solid
from petrify.solid import tau, Point, Vector, Basis, PlanarPolygon, Extrusion

class TestUtilities(unittest.TestCase):
    def test_perpendicular(self):
        right = tau / 4
        def _t(v):
            o = solid.perpendicular(v)
            self.assertEqual(o.angle(v), right)

        _t(Vector(1, 0, 0))
        _t(Vector(0, 1, 0))
        _t(Vector(0, 0, 1))

        _t(Vector(1, 1, 0))
        _t(Vector(1, 0, 1))
        _t(Vector(0, 1, 1))

        _t(Vector(1, 1, 1))

class TestExtrusion(unittest.TestCase):
    def test_simple(self):
        parallelogram = plane.Polygon([
            plane.Point(0, 0),
            plane.Point(0, 1),
            plane.Point(1, 2),
            plane.Point(1, 1)
        ])
        square = plane.Polygon([
            plane.Point(0, 0),
            plane.Point(0, 1),
            plane.Point(1, 1),
            plane.Point(1, 0)
        ])
        object = Extrusion([
            PlanarPolygon(Basis.xy, parallelogram),
            PlanarPolygon(Basis.xy + Vector(0, 0, 1), square),
        ])

    def test_simplification(self):
        triangle = plane.Polygon([
            plane.Point(0, 0),
            plane.Point(0, 1),
            plane.Point(0, 1),
            plane.Point(1, 1)
        ])
        square = plane.Polygon([
            plane.Point(0, 0),
            plane.Point(0, 1),
            plane.Point(1, 1),
            plane.Point(1, 0)
        ])
        dz = Vector.basis.z
        final = Extrusion([
            PlanarPolygon(Basis.xy, square),
            PlanarPolygon(Basis.xy + dz, triangle),
            PlanarPolygon(Basis.xy + 2 * dz, square),
        ])
        self.assertEqual(set(len(p.points) for p in final.polygons), set([3, 4]))

class TestNode(unittest.TestCase):
    def test_addition(self):
        a = solid.Box(Vector(0, 0, 0), Vector(3, 3, 1))
        b = solid.Box(Vector(1, 1, 0.5), Vector(1, 1, 3))

        combined = a + b
        self.assertTrue(len(combined.polygons) > len(a.polygons) + len(b.polygons))

    def test_subtraction(self):
        a = solid.Box(Vector(0, 0, 0), Vector(3, 3, 1))
        b = solid.Box(Vector(1, 1, 0.5), Vector(1, 1, 3))

        combined = a - b.translate(Vector(0, 0, -0.25))
        self.assertTrue(len(combined.polygons) > len(a.polygons) + len(b.polygons))

        self.assertEqual((a - Vector(1, 2, 3)).envelope().origin, Point(-1, -2, -3))

    def test_division(self):
        a = solid.Box(Vector(0, 0, 0), Vector(2, 2, 2))

        scaled = a / 2
        self.assertEqual(scaled.envelope().size(), Vector(1, 1, 1))

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(solid))
    return tests
