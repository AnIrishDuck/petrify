import doctest, unittest
from petrify import solid
from petrify.solid import tau, Vector

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

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(solid))
    return tests
