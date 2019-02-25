import doctest, unittest
from petrify.formats import svg
from petrify.solid import Projection

class TestParse(unittest.TestCase):
    def test_example(self):
        shapes = svg.parse(open('tests/fixtures/example.svg'))
        self.assertEqual(len(shapes['rect'].polygons()), 2)

class TestExtrusion(unittest.TestCase):
    def test_example(self):
        paths = svg.parse('tests/fixtures/example.svg')
        box = paths['rect']
        example = svg.PathExtrusion(box, 1.0, Projection.unit)

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(svg))
    return tests
