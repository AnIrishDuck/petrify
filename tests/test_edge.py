import doctest, unittest

from petrify import edge
from petrify.edge import Chamfer, EdgeChamfer, edge_inset, polygon_inset
from petrify.solid import Box, Vector, Point
from petrify.space import LineSegment, Polygon

class TestInset(unittest.TestCase):
    def test_edge_inset(self):
        inwards = Vector(0.1, 0, 0)
        edge = Vector(1, 0, 0)
        normal = Vector(0, 0, 1)

        inset = edge_inset(edge, inwards, normal)
        self.assertEqual(inset.xyz, (0.1, 0, 0))

        inwards = Vector(0.5, 0, 0)
        edge = Vector(1, -1, 0)
        normal = Vector(0, 0, 1)

        inset = edge_inset(edge, inwards, normal)
        self.assertEqual(inset.xyz, (0.5, -0.5, 0))

    def test_polygon_inset(self):
        inwards = Vector(0, 0.5, 0)
        points = [
            Point(1, 3, 0),
            Point(2, 2, 0),
            Point(3, 2, 0),
            Point(4, 3, 0),
        ]
        normal = Vector(0, 0, 1)
        edge = LineSegment(points[1], points[2])
        polygon = Polygon(points)
        edge = polygon_inset(polygon, edge, inwards)

        self.assertEqual(edge.p1.xyz, (3.5, 2.5, 0))
        self.assertEqual(edge.p2.xyz, (1.5, 2.5, 0))

    def test_polygon_inset_cut_a(self):
        inwards = Vector(0.00, 0.10, 0.00)
        points = [
            Point(0, 0, 0),
            Point(0, 1, 0),
            Point(1, 1, 0),
            Point(1, 0, 0),
        ]
        normal = Vector(0, 0, -1)
        edge = LineSegment(points[-1], points[0])
        polygon = Polygon(points)
        edge = polygon_inset(polygon, edge, inwards)

        self.assertEqual(edge.p1.xyz, (0, 0.1, 0))
        self.assertEqual(edge.p2.xyz, (1, 0.1, 0))

    def test_cut(self):
        cube = Box(Vector(0, 0, 0), Vector(1, 1, 1))
        edge = LineSegment(Point(0, 0, 0), Point(1, 0, 0))

        chamfer = EdgeChamfer(cube.polygons, edge, 0.1)
        polygons = [*chamfer.insets(), chamfer.start_cap(), chamfer.end_cap()]
        normals = [p.plane.normal for p in cube.polygons]

        for p in polygons:
            normal = p.plane.normal
            self.assertIn(normal, normals)

    def assertValidPoints(self, solid):
        for polygon in solid.polygons:
            for p in polygon.points:
                self.assertIn(round(p.x, 2), [0, 1, 0.1, 0.9])
                self.assertIn(round(p.y, 2), [0, 1, 0.1, 0.9])
                self.assertIn(round(p.z, 2), [0, 1, 0.1, 0.9])

    def test_partial_chamfer(self):
        cube = Box(Vector(0, 0, 0), Vector(1, 1, 1))
        edges = [
            LineSegment(Point(0, 0, 0), Point(1, 0, 0)),
            LineSegment(Point(1, 0, 0), Point(1, 1, 0))
        ]

        chamfer = Chamfer(cube, edges, 0.1)
        self.assertValidPoints(cube - chamfer)

    def test_full_chamfer(self):
        cube = Box(Vector(0, 0, 0), Vector(1, 1, 1))
        edges = [
            LineSegment(Point(0, 0, 0), Point(1, 0, 0)),
            LineSegment(Point(1, 0, 0), Point(1, 1, 0)),
            LineSegment(Point(1, 1, 0), Point(0, 1, 0)),
            LineSegment(Point(0, 1, 0), Point(0, 0, 0))
        ]

        chamfer = Chamfer(cube, edges, 0.1)
        self.assertValidPoints(cube - chamfer)

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(edge))
    return tests
