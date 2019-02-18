import doctest, unittest
from petrify.formats import svg

class TestParse(unittest.TestCase):
    def test_example(self):
        shapes = svg.parse(open('tests/fixtures/example.svg'))
        self.assertEqual(len(shapes['rect'].polygons()), 2)

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(svg))
    return tests
