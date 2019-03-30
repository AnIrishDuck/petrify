import doctest, unittest
from petrify.formats import stl
from petrify.solid import Projection

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(stl))
    return tests
