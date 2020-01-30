import doctest
import unittest

from petrify import generic, space
from petrify.space import Point, Vector

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(space))
    tests.addTests(doctest.DocTestSuite(space.point))
    tests.addTests(doctest.DocTestSuite(space.transform))
    return tests

class VectorTests(unittest.TestCase):
    def test_generic_instance(self):
        self.assertTrue(isinstance(Vector(1, 1, 1), Vector))
        self.assertTrue(isinstance(Vector(1, 1, 1), generic.Vector))

    def test_angle(self):
        a = Vector(0.11176897466954505, 0.056949137058031396, 0.0)
        b = Vector(0.016835599543175706, 0.008578166424744738, 0.0)
        a.angle(b)

class PointTests(unittest.TestCase):
    def test_generic_instance(self):
        self.assertTrue(isinstance(Point(1, 1, 1), Point))
        self.assertTrue(isinstance(Point(1, 1, 1), generic.Point))

    def test_difference(self):
        self.assertEqual(Point.origin - Vector(1, 2, 3), Point(-1, -2, -3))
        self.assertEqual(Point.origin - [1, 2, 3], Point(-1, -2, -3))

    def test_operation(self):
        self.assertEqual(Point(2, 4, 6) / 2, Point(1, 2, 3))

    def test_negation(self):
        self.assertEqual(-Point(2, 4, 6), Point(-2, -4, -6))

    def test_normalized(self):
        self.assertEqual(Point(0, 4, 0).normalized(), Point(0, 1, 0))
