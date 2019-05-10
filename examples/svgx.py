from petrify.solid import Projection
from petrify.formats import SVG, STL
from petrify.formats.svg import PathExtrusion

def shape():
    paths = SVG.read('tests/fixtures/example.svg', 'mm')
    box = paths['rect']
    return PathExtrusion(box, 100.0, Projection.unit)

if __name__ == '__main__':
    STL('output/svg.stl', 'mm').write(shape().as_unit('mm'))
