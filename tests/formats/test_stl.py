import doctest, unittest
from petrify.formats import stl

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(stl))
    return tests
