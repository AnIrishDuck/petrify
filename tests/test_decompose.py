import unittest

from petrify import decompose, space
from petrify.plane import Point, LineSegment, Polygon
from petrify.solid import Node, Cylinder

class TestTrapezoid(unittest.TestCase):
    def test_square(self):
        square = Polygon([
            Point(0, 0),
            Point(0, 1),
            Point(1, 1),
            Point(1, 0),
        ])
        polygons = decompose.trapezoidal([square])
        self.assertEqual([p.points for p in polygons], [
            [
                Point(0, 0),
                Point(0, 1),
                Point(1, 1),
                Point(1, 0)
            ],
        ])

    def test_double_diamond(self):
        diamond = Polygon([
            Point(1, 0),
            Point(2, 1),
            Point(1, 2),
            Point(0, 1),
        ])
        double = [diamond, diamond + Point(3, 0.1)]
        polygons = decompose.trapezoidal(double)

    def test_complex(self):
        f = Polygon([
            Point(0, 0),
            Point(0, 7),
            Point(4, 7),
            Point(4, 5),
            Point(2, 5),
            Point(2, 4),
            Point(4, 4),
            Point(4, 2),
            Point(2, 2),
            Point(2, 0)
        ])

        polygons = decompose.trapezoidal([f])
        self.assertEqual([p.points for p in polygons], [
            [
                Point(0, 0),
                Point(0, 2),
                Point(2, 2),
                Point(2, 0)
            ],
            [
                Point(0, 2),
                Point(0, 4),
                Point(4, 4),
                Point(4, 2)
            ],
            [
                Point(0, 4),
                Point(0, 5),
                Point(2, 5),
                Point(2, 4)
            ],
            [
                Point(0, 5),
                Point(0, 7),
                Point(4, 7),
                Point(4, 5)
            ]
        ])

        inverted = Polygon([Point(p.y, p.x) for p in f.points])
        polygons = decompose.trapezoidal([inverted])
        self.assertEqual([p.points for p in polygons], [
            [Point(7.0, 0.0), Point(7.0, 2.0), Point(0.0, 2.0), Point(0.0, 0.0)],
            [Point(2.0, 2.0), Point(2.0, 4.0), Point(4.0, 4.0), Point(4.0, 2.0)],
            [Point(5.0, 2.0), Point(5.0, 4.0), Point(7.0, 4.0), Point(7.0, 2.0)]
        ])

    def test_embedded(self):
        square = Polygon([
            Point(0, 0),
            Point(0, 10),
            Point(10, 10),
            Point(10, 0),
        ])
        inner = Polygon([
            Point(4, 4),
            Point(4, 6),
            Point(6, 6),
            Point(6, 4)
        ])
        polygons = decompose.trapezoidal([square, inner])
        self.assertEqual([p.points for p in polygons], [
            [
                Point(0.0, 0.0),
                Point(0.0, 4.0),
                Point(10.0, 4.0),
                Point(10.0, 0.0)
            ],
            [
                Point(0.0, 4.0),
                Point(0.0, 6.0),
                Point(4.0, 6.0),
                Point(4.0, 4.0)
            ],
            [
                Point(6.0, 4.0),
                Point(6.0, 6.0),
                Point(10.0, 6.0),
                Point(10.0, 4.0)
            ],
            [
                Point(0.0, 6.0),
                Point(0.0, 10.0),
                Point(10.0, 10.0),
                Point(10.0, 6.0)
            ]
        ])


    def test_v_counter(self):
        v = Polygon([
            Point(2, 0),
            Point(0, 4),
            Point(1, 4),
            Point(2, 1),
            Point(3, 4),
            Point(4, 4),
        ])

        polygons = decompose.trapezoidal(v.to_counterclockwise().polygons)
        self.assertEqual([p.points for p in polygons], [
            [Point(1.5, 1.0), Point(2.5, 1.0), Point(2.0, 0.0)],
            [Point(1.5, 1.0), Point(0.0, 4.0), Point(1.0, 4.0), Point(2.0, 1.0)],
            [Point(2.0, 1.0), Point(3.0, 4.0), Point(4.0, 4.0), Point(2.5, 1.0)]
        ])

def rect(a, b):
    return Polygon([a, Point(a.x, b.y), b, Point(b.x, a.y)])

class TestFragmentation(unittest.TestCase):
    def test_simple(self):
        polygons = [
            rect(Point(0, 0), Point(1, 1)),
            rect(Point(1, 0), Point(2, 2))
        ]

        segments = [l for p in polygons for l in p.segments()]
        fragments = [LineSegment(l.p1, l.p2) for l in decompose.fragment(segments)]
        self.assertEqual(set(fragments) - set(segments), set([
            LineSegment(Point(1, 0), Point(1, 1)),
            LineSegment(Point(1, 1), Point(1, 2))
        ]))

        self.assertEqual(set(segments) - set(fragments), set([
            LineSegment(Point(1, 0), Point(1, 2))
        ]))

    def test_multi_frag(self):
        polygons = [
            rect(Point(0, 0), Point(5, 1)),
            rect(Point(0, 1), Point(1, 2)),
            rect(Point(2, 1), Point(3, 2)),
            rect(Point(4, 1), Point(5, 2)),
        ]

        segments = [l for p in polygons for l in p.segments()]
        fragments = [LineSegment(l.p1, l.p2) for l in decompose.fragment(segments)]
        self.assertEqual(set(fragments) - set(segments), set([
            LineSegment(Point(0, 1), Point(1, 1)),
            LineSegment(Point(1, 1), Point(2, 1)),
            LineSegment(Point(2, 1), Point(3, 1)),
            LineSegment(Point(3, 1), Point(4, 1)),
            LineSegment(Point(4, 1), Point(5, 1))
        ]))

        self.assertEqual(set(segments) - set(fragments), set([
            LineSegment(Point(0, 1), Point(5, 1))
        ]))

def reset(polygon, point):
    points = polygon.points
    ix = points.index(point)
    return points[ix:] + points[:ix]

class TestPolygons(unittest.TestCase):
    def test_simple(self):
        polygons = [
            rect(Point(0, 0), Point(1, 1)),
            rect(Point(1, 0), Point(2, 2))
        ]

        polygon, = decompose.rebuild(polygons)
        self.assertEqual(reset(polygon, Point(0, 0)), [
            Point(0, 0), Point(0, 1), Point(1, 1),
            Point(1, 2), Point(2, 2), Point(2, 0)
        ])

    def test_multi_frag(self):
        polygons = [
            rect(Point(0, 0), Point(5, 1)),
            rect(Point(0, 1), Point(1, 2)),
            rect(Point(2, 1), Point(3, 2)),
            rect(Point(4, 1), Point(5, 2)),
        ]

        segments = [l for p in polygons for l in p.segments()]
        polygon, = decompose.rebuild(polygons)
        self.assertEqual(reset(polygon, Point(0, 0)), [
            Point(0, 0),
            Point(0, 2), Point(1, 2), Point(1, 1),
            Point(2, 1), Point(2, 2), Point(3, 2), Point(3, 1),
            Point(4, 1), Point(4, 2), Point(5, 2),
            Point(5, 0),
        ])

segments = 5
class Tube(Node):
    def __init__(self, inner_diameter, outer_diameter, height):
        self.outer = Cylinder(
            space.Point.origin,
            space.Vector(0, 0, height),
            outer_diameter / 2,
            segments = segments
        )

        self.inner = Cylinder(
            space.Point.origin,
            space.Vector(0, 0, height),
            inner_diameter / 2,
            segments = segments
        )

        super().__init__((self.outer - self.inner).polygons)

class TestRecreation(unittest.TestCase):
    def test_ring_recreation(self):
        port = 2.65
        outer = 2.28
        inner = 2.22
        wall = 0.125

        smaller = Tube(inner - wall * 2, inner, 1.5)
        bigger = Tube(inner - wall * 2, outer, 1.5) + space.Vector(0, 0, 1.5 - wall)

        holster_top = Tube(inner - wall, port + wall * 2, 0.75)
        holster = Tube(port, port + wall * 2, 1.25) + holster_top.translate(space.Vector(0, 0, 1.0))

        adaptor = smaller + holster + bigger

        polygons = [p for p in adaptor.polygons if p.plane.normal.snap(0.1) == space.Vector.basis.z]
        middle = [p for p in polygons if p.points[0].z == 1.75]
        recreated = decompose.rebuild(middle)

        self.assertEqual(len(recreated), 2)
        for polygon in recreated:
            self.assertEqual(len(polygon.segments()), segments)
