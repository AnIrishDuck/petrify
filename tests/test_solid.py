import doctest, unittest
from petrify import u, plane, solid
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

class TestCollection(unittest.TestCase):
    def test_addition(self):
        a = solid.Box(Point(0, 0, 0), Vector(1, 1, 1)).view(color='red')
        b = solid.Box(Point(0, 0, 2), Vector(1, 1, 1)).view(color='blue')
        collection = solid.Collection([a, b]) + Vector.basis.x

        self.assertEqual(
            [n.view_data for n in collection.nodes],
            [{'color': 'red'}, {'color': 'blue'}]
        )

    def test_subtraction(self):
        a = solid.Box(Point(0, 0, 0), Vector(1, 1, 1))
        b = solid.Box(Point(0, 0, 2), Vector(1, 1, 1))
        collection = solid.Collection([a, b])
        cut = solid.Box(Point(0.25, 0.25, 0.25), Vector(0.5, 0.5, 2))

        collection = collection - cut
        inset = Vector(0.05, 0.05, 0.05)
        inside = solid.Box(cut.origin + inset, cut.size() - (inset * 2))
        for n in collection.nodes:
            self.assertTrue(len((n * inside).polygons) == 0)

    def test_multiplication(self):
        a = solid.Box(Point(0, 0, 0), Vector(1, 1, 1)).view(color='red')
        b = solid.Box(Point(0, 0, 2), Vector(1, 1, 1))
        collection = solid.Collection([a, b])
        common = solid.Box(Point(0.25, 0.25, 0.25), Vector(0.5, 0.5, 2))

        collection = collection * common
        self.assertEqual(len(collection.nodes), 2)
        self.assertEqual(collection.nodes[0].view_data, {'color': 'red'})

        collection = solid.Collection([a, b])
        common = solid.Box(Point(0.25, 0.25, 0.25), Vector(0.5, 0.5, 0.5))
        self.assertTrue(len(collection.nodes), 1)

        shift_units = (collection * u.cm).m_as(u.mm)
        self.assertEqual(shift_units.envelope().size(), Vector(10, 10, 30))

    def test_view_recursion(self):
        a = solid.Box(Point(0, 0, 0), Vector(1, 1, 1))
        b = solid.Box(Point(0, 0, 2), Vector(1, 1, 1))
        collection = solid.Collection([a.view(color='red'), b])
        self.assertEqual(
            collection.view(opacity=0.5).nodes[0].view_data,
            {'color': 'red', 'opacity': 0.5}
        )

    def test_inner_methods(self):
        a = solid.Box(Point(0, 0, 0), Vector(1, 1, 1)).view(color='red')
        b = solid.Box(Point(0, 0, 2), Vector(1, 1, 1)).view(color='blue')
        c = solid.Collection([a, b]) + Vector.basis.x

        original = [{'color': 'red'}, {'color': 'blue'}]

        def _vd(c): return [n.view_data for n in c.nodes]

        self.assertEqual(_vd(c.scale(Vector(2, 2, 2))), original)
        self.assertEqual(_vd(c.translate(Vector(1, 2, 3))), original)
        self.assertEqual(_vd(c.rotate(Vector.basis.z, tau / 3)), original)
        self.assertEqual(_vd(c.rotate_at(Point(1, 1, 1), Vector.basis.z, tau / 3)), original)

class TestView(unittest.TestCase):
    def test_recursion(self):
        a = solid.Box(Point(0, 0, 0), Vector(1, 1, 1))
        view = a.view(color='red').view(opacity=0.5).view(color='blue')
        self.assertEqual(view.view_data, {'color': 'blue', 'opacity': 0.5})

    def test_inner_methods(self):
        original = {'color': 'red'}
        a = solid.Box(Point(0, 0, 0), Vector(1, 1, 1)).view(**original)
        b = solid.Box(Point(0.25, 0.25, 0.25), Vector(0.5, 0.5, 2))

        self.assertEqual((a + b).view_data, original)
        self.assertEqual((a * b).view_data, original)
        self.assertEqual((a / 2).view_data, original)
        self.assertEqual((a - b).view_data, original)

        self.assertEqual(a.scale(Vector(2, 2, 2)).view_data, original)
        self.assertEqual(a.translate(Vector(1, 2, 3)).view_data, original)
        self.assertEqual(a.rotate(Vector.basis.z, tau / 3).view_data, original)
        self.assertEqual(a.rotate_at(Point(1, 1, 1), Vector.basis.z, tau / 3).view_data, original)

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(solid))
    return tests
