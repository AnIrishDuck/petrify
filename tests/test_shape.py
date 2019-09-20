import doctest
from petrify import shape

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(shape))
    return tests
