import unittest
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
