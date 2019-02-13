import doctest
from petrify import conversions

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(conversions))
    return tests
