import doctest

from petrify import plane

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(plane))
    return tests
