from petrify.solid import Projection
from petrify.formats import svg, SVG, STL

def shape():
    paths = SVG.read('tests/fixtures/example.svg', 'mm')
    box = paths['rect']
    return svg.PathExtrusion(box, 100.0, Projection.unit)

if __name__ == '__main__':
    STL('output/svg.stl', 'mm').write(shape().as_unit('mm'))
