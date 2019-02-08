import unittest
from petrify.edge import Chamfer, edge_inset, polygon_inset
from petrify.solid import Box, Vector3, Point3
from petrify.euclid import LineSegment3
from petrify.three import Polygon

class TestInset(unittest.TestCase):
    def test_edge_inset(self):
        inwards = Vector3(0.1, 0, 0)
        edge = Vector3(1, 0, 0)
        normal = Vector3(0, 0, 1)

        inset = edge_inset(edge, inwards, normal)
        self.assertEqual(inset.xyz, (0.1, 0, 0))

        inwards = Vector3(0.5, 0, 0)
        edge = Vector3(1, -1, 0)
        normal = Vector3(0, 0, 1)

        inset = edge_inset(edge, inwards, normal)
        self.assertEqual(inset.xyz, (0.5, -0.5, 0))

    def test_polygon_inset(self):
        inwards = Vector3(0, 0.5, 0)
        points = [
            Point3(1, 3, 0),
            Point3(2, 2, 0),
            Point3(3, 2, 0),
            Point3(4, 3, 0),
        ]
        normal = Vector3(0, 0, 1)
        edge = LineSegment3(points[1], points[2])
        polygon = Polygon(points, normal)
        edge = polygon_inset(polygon, edge, inwards)

        self.assertEqual(edge.p1.xyz, (3.5, 2.5, 0))
        self.assertEqual(edge.p2.xyz, (1.5, 2.5, 0))

    def test_polygon_inset_cut_a(self):
        inwards = Vector3(0.00, 0.10, 0.00)
        points = [
            Point3(0, 0, 0),
            Point3(0, 1, 0),
            Point3(1, 1, 0),
            Point3(1, 0, 0),
        ]
        normal = Vector3(0, 0, -1)
        edge = LineSegment3(points[-1], points[0])
        polygon = Polygon(points, normal)
        edge = polygon_inset(polygon, edge, inwards)

        self.assertEqual(edge.p1.xyz, (0, 0.1, 0))
        self.assertEqual(edge.p2.xyz, (1, 0.1, 0))

    def test_cut(self):
        cube = Box(Vector3(0, 0, 0), Vector3(1, 1, 1))
        edge = LineSegment3(Point3(0, 0, 0), Point3(1, 0, 0))

        def to_euclid(v):
            return Vector3(v.x, v.y, v.z)

        chamfer = Chamfer(cube, edge, 0.1)
        polygons = [*chamfer.insets, *chamfer.endcaps]
        normals = [to_euclid(p.plane.normal) for p in cube.polygons]

        for p in polygons:
            normal = to_euclid(p.plane.normal)
            self.assertIn(normal, normals)
