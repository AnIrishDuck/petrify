import doctest, unittest
from petrify.formats import svg, SVG
from petrify.solid import Projection
from petrify import u

class TestParse(unittest.TestCase):
    def test_example(self):
        shapes = SVG.read(open('tests/fixtures/example.svg'), 'mm')
        self.assertEqual(len(shapes['rect'].polygons()), 2)

class TestExtrusion(unittest.TestCase):
    def test_example(self):
        paths = SVG.read('tests/fixtures/example.svg', 1 * u.inches / u.file)
        box = paths['rect']
        example = svg.PathExtrusion(box, 1.0, Projection.unit)

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(svg))
    return tests
