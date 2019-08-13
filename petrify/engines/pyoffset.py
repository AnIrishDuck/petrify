from ..plane import ComplexPolygon

def offset(polygon, amount):
    def off(ps, v):
        polygons = [p.offset(v) for p in ps]
        return [p for p in polygons if p is not None]

    return ComplexPolygon(
        interior=off(polygon.interior, -amount),
        exterior=off(polygon.exterior, amount)
    )
