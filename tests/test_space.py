import doctest

from petrify import space

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(space))
    return tests
