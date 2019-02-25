from petrify.solid import Projection
from petrify.formats import svg

def shape():
    paths = svg.parse('tests/fixtures/example.svg')
    box = paths['rect']
    return svg.PathExtrusion(box, 100.0, Projection.unit)

if __name__ == '__main__':
    shape().to_stl('output/svg.stl')
