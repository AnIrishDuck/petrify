"""
Geometry geared towards modifying object edges.

>>> from petrify.solid import Box, Vector, Point
>>> from petrify.space import LineSegment
>>> box = Box(Point.origin, Vector(1, 1, 1))
>>> edge = LineSegment(Point(0, 0, 0), Point(0, 1, 0))
>>> chamfered = box - Chamfer(box, [edge], 0.25)

"""
from .solver import solve_matrix
from .solid import tau, Node, Union
from .space import LineSegment, Polygon

from csg import core, geom

class Chamfer(Union):
    """
    Chamfer geometry formed by creating an inset of `amount` along
    the pairs of polygons formed by `edges` on a `solid`.

    The starting point of each `edge` must equal the endpoint of the prior edge
    (and, by induction, the endpoint of each `edge` must be the start of the
    next edge).

    """
    def __init__(self, solid, edges, amount):
        polygons = solid.polygons
        for before, e in zip(edges, edges[1:]):
            assert(before.p2 == e.p1)
        chamfers = [EdgeChamfer(polygons, edge, amount) for edge in edges]
        super().__init__(chamfers)

class EdgeChamfer(Node):
    def __init__(self, polygons, edge, amount):
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
            # diagonal
            Polygon([a_inset.p2, a_inset.p1, b_inset.p2, b_inset.p1]),
            # start cap
            Polygon([a_edge.p1, a_inset.p2, b_inset.p1]),
            # end cap
            Polygon([a_inset.p1, a_edge.p2, b_inset.p2])
        ])

    def insets(self):
        return self.polygons[0:2]

    def diagonal(self):
        return self.polygons[2]

    def start_cap(self):
        return self.polygons[3]

    def end_cap(self):
        return self.polygons[4]

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
