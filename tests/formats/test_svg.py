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
        self.assertEqual(len(box.polygon().interior), 1)
        self.assertEqual(len(box.polygon().exterior), 1)

    def test_conversion(self):
        scale = 1 * u.inches / u.file
        paths = SVG.read('tests/fixtures/example.svg', scale)
        paths['text'].polygon()
        paths['text'].polygon(1.0 * u.file)
        paths['text'].polygons()
        paths['text'].polygons(1.0 * u.mm / scale)

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(svg))
    return tests
