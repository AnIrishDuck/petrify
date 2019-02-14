import unittest

from petrify import decompose
from petrify.plane import Point

class TestUtilities(unittest.TestCase):
    def test_decompose(self):
        f = [
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
        ]

        polygons = decompose.trapezoidal(f)
        self.assertEqual(polygons, [
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

        inverted = [Point(p.y, p.x) for p in f]
        self.assertEqual(decompose.trapezoidal(inverted), [
            [Point(7.0, 0.0), Point(7.0, 2.0), Point(0.0, 2.0), Point(0.0, 0.0)],
            [Point(4.0, 2.0), Point(4.0, 4.0), Point(2.0, 4.0), Point(2.0, 2.0)],
            [Point(7.0, 2.0), Point(7.0, 4.0), Point(5.0, 4.0), Point(5.0, 2.0)]
        ])
