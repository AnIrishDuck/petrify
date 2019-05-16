from petrify.solid import Basis, Vector
from petrify.formats import SVG, STL
from petrify.formats.svg import PathExtrusion

def shape():
    paths = SVG.read('tests/fixtures/example.svg', 'mm')
    box = paths['rect']
    return PathExtrusion(Basis.unit, box, Vector.basis.z * 10)

if __name__ == '__main__':
    STL('output/svg.stl', 'mm').write(shape().as_unit('mm'))
