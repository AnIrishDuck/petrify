from csg import core, geom
from ..space import Point, Polygon

def from_pycsg(_csg):
    def from_csg_polygon(csg):
        points = [Point(v.pos.x, v.pos.y, v.pos.z) for v in csg.vertices]
        return Polygon(points)
    return [from_csg_polygon(p) for p in (_csg if isinstance(_csg, list) else _csg.toPolygons())]

def to_pycsg(polygons):
    def to_csg_polygon(polygon):
        vertices = [geom.Vertex(geom.Vector(p.x, p.y, p.z)) for p in polygon.points]
        return geom.Polygon(vertices)
    return core.CSG.fromPolygons([to_csg_polygon(p) for p in polygons])

def union(*solids):
    whole = to_pycsg(solids[0])
    for polygons in solids[1:]:
        whole = whole.union(to_pycsg(polygons))
    return from_pycsg(whole)

def intersect(a, b):
    return from_pycsg(to_pycsg(a).intersect(to_pycsg(b)))

def subtract(a, b):
    return from_pycsg(to_pycsg(a).subtract(to_pycsg(b)))
