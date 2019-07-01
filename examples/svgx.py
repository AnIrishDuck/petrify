from petrify.solid import Basis, Vector, PolygonExtrusion, PlanarPolygon
from petrify.formats import SVG, STL

def shape():
    paths = SVG.read('tests/fixtures/example.svg', 'mm')
    box = paths['rect'].polygon()
    return PolygonExtrusion(PlanarPolygon(Basis.xy, box), Vector.basis.z * 10)

if __name__ == '__main__':
    STL('output/svg.stl', 'mm').write(shape().as_unit('mm'))
