import doctest
import unittest

from petrify import space
from petrify.space import Vector

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(space))
    return tests

class VectorTests(unittest.TestCase):
    def test_angle(self):
        a = Vector(0.11176897466954505, 0.056949137058031396, 0.0)
        b = Vector(0.016835599543175706, 0.008578166424744738, 0.0)
        a.angle(b)
