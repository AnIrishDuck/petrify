import doctest, unittest

from petrify import generic

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(generic))
    return tests
