"""
Edge treatments.

Treatments return the original object with modified geometry. All nominal
object properties are unchanged:

>>> box = Box(Vector(1, 1, 1), Vector(1, 1, 1))
>>> chamfered = chamfer(box, box.edges)
>>> chamfered.size
Vector(1, 1, 1)

"""
from .solver import solve_matrix
from .solid import tau, Node
from .space import LineSegment, Polygon

from csg import core, geom

class Chamfer(Node):
    """
    Chamfer cut geometry by creating an inset of `amount` along
    both polygons formed by `edge` on a `solid`.

    """
    def __init__(self, solid, edge, amount):
        polygons = solid.polygons
        faces = [p for p in polygons if p.has_edge(edge)]
        assert(len(faces) == 2)
        a, b = faces

        a_normal = a.plane.normal
        b_normal = b.plane.normal

        a_edge, = [l for l in a.segments() if l == edge]
        b_edge, = [l for l in b.segments() if l == edge]

        assert(a_normal.angle(edge.v) == tau / 4)
        assert(b_normal.angle(edge.v) == tau / 4)

        direction_a = b_normal.rotate_around(b_edge.v, a_normal.angle(b_normal) - tau / 4)
        direction_b = a_normal.rotate_around(a_edge.v, b_normal.angle(a_normal) - tau / 4)
        a_inset = polygon_inset(a, a_edge, -direction_a.normalized() * amount)
        b_inset = polygon_inset(b, b_edge, -direction_b.normalized() * amount)

        super().__init__([
            # insets
            Polygon([a_edge.p1, a_edge.p2, a_inset.p1, a_inset.p2]),
            Polygon([b_edge.p1, b_edge.p2, b_inset.p1, b_inset.p2]),
            # cut
            Polygon([a_inset.p2, a_inset.p1, b_inset.p2, b_inset.p1]),
            # endcaps
            Polygon([a_inset.p1, a_edge.p2, b_inset.p2]),
            Polygon([a_edge.p1, a_inset.p2, b_inset.p1]),
        ])

    @property
    def insets(self):
        return self.polygons[0:2]

    @property
    def cut(self):
        return self.polygon[2]

    @property
    def endcaps(self):
        return self.polygons[3:]

def polygon_inset(polygon, edge, inwards):
    """
    Finds the inset line given a normal direction, the polygon to inset, and the
    edge to inset from.

    Note: it is *critical* that `edge` face in the same direction as it does for
    the `polygon`.

    """
    segments = polygon.segments()
    before, = [l for l in segments if l.touches(edge.p1) and l != edge]
    after, = [l for l in segments if l.touches(edge.p2) and l != edge]

    before_inset = edge_inset(edge.p1 - before.p1, inwards, polygon.plane.normal)
    after_inset = edge_inset(edge.p2 - after.p2, inwards, polygon.plane.normal)

    return LineSegment(edge.p2 + after_inset, edge.p1 + before_inset)

def edge_inset(edge, inwards, normal):
    lateral = inwards.cross(normal)
    # lateral vector moving from the inwards vector must intersect with the edge
    # vector on the plane. Because of slop, it might not be exactly on the plane.
    # Add the plane normal to fully define the vector space:
    # inward + u * lateral + v * normal = w * edge
    # w * edge - u * lateral - v * normal = inward
    rows = list(zip(edge.xyz, (-lateral).xyz, (-normal).xyz, inwards.xyz))
    matrix = list(list(row) for row in rows)
    solution = solve_matrix(matrix)
    scale = solution[0]
    return scale * edge
