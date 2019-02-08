from .euclid import Point3, LineSegment3

def to_euclid(csg):
    return Point3(csg.x, csg.y, csg.z)

class Polygon:
    """ Polygons are a linear cycle of coplanar convex points. """

    def __init__(self, points, normal):
        self.points = points
        self.normal = normal

    def segments(self):
        paired = zip(self.points, self.points[1:] + [self.points[0]])
        return [LineSegment3(a, b) for a, b in paired]

    def has_edge(self, edge):
        return any(l == edge for l in self.segments())

    @classmethod
    def from_pycsg(self, csg):
        points = [to_euclid(v.pos) for v in csg.vertices]
        normal = to_euclid(csg.plane.normal).vector()
        return Polygon(points, normal)

    def __repr__(self):
        return "Polygon({0!r}, {1!r})".format(self.points, self.normal)
