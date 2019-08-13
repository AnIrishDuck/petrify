import pyclipper
from ..plane import ComplexPolygon, Point, Polygon

def offset(polygon, distance):
    solution = []
    for offset, polygons in ((1, polygon.interior), (-1, polygon.exterior)):
        for simple in polygons:
            pco = pyclipper.PyclipperOffset()
            raw = [(p.x, p.y) for p in simple.points]
            pco.AddPath(raw, pyclipper.JT_MITER, pyclipper.ET_CLOSEDPOLYGON)
            solution.extend(pco.Execute(offset * distance))

    final = [Polygon([Point(x, y) for x, y in p]) for p in solution]
    return ComplexPolygon(final)
