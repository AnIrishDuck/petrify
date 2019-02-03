import unittest
from petrify import solid
from petrify.solid import tau, Vector3

class TestUtilities(unittest.TestCase):
    def test_perpendicular(self):
        right = tau / 4
        def _t(v):
            o = solid.perpendicular(v)
            self.assertEqual(o.angle(v), right)

        _t(Vector3(1, 0, 0))
        _t(Vector3(0, 1, 0))
        _t(Vector3(0, 0, 1))

        _t(Vector3(1, 1, 0))
        _t(Vector3(1, 0, 1))
        _t(Vector3(0, 1, 1))

        _t(Vector3(1, 1, 1))
