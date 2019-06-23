from petrify.geometry import tau
from petrify.space import Vector
from petrify.solid import Collection, Node, PlanarPolygon, Polygon

def render(thing):
    if isinstance(thing, list):
        if isinstance(thing[0], Node):
            return render_solid(Collection(list))
        elif isinstance(thing[0], PlanarPolygon):
            return render_polygons(thing)
        elif isinstance(thing[0], Polygon):
            return render_polygons(thing)
    elif isinstance(thing, Node):
        return render_solid(thing)
    elif isinstance(thing, PlanarPolygon):
        return render_polygons([thing])

    raise NotImplemented

def render_solid(solid):
    rotated = (
        solid.rotate_around(tau / 8, Vector.basis.x)
             .rotate_around(tau / 8, Vector.basis.y)
    )
    return rotated.visualize()

def render_polygons(all_polygons):
    import pythreejs as js
    import numpy as np

    lines = []
    line_colors = []

    red = [1, 0, 0]
    green = [0, 1, 0]
    for p in all_polygons:
        if isinstance(p, Polygon):
            exterior = [p]
            interior = []
        if isinstance(p, PlanarPolygon):
            exterior = p.project(exterior=True)
            interior = p.project(exterior=False)
        for color, polygons in zip([green, red], [exterior, interior]):
            for polygon in polygons:
                for segment in polygon.segments():
                    lines.extend([segment.p1, segment.p2])
                    line_colors.extend([color, color])

    lines = np.array(lines, dtype=np.float32)
    line_colors = np.array(line_colors, dtype=np.float32)
    geometry = js.BufferGeometry(
        attributes={
            'position': js.BufferAttribute(lines, normalized=False),
            'color': js.BufferAttribute(line_colors, normalized=False),
        },
    )
    material = js.LineBasicMaterial(vertexColors='VertexColors', linewidth=1)
    return js.LineSegments(geometry, material)
