import math

from .plane import Polygon, Point, Vector
from .geometry import tau

class Rectangle(Polygon):
    """
    An axis-aligned rectangle with a point of `origin` and a vector `size`:

    >>> square = Rectangle(Point.origin, Vector(1, 1))

    """

    def __init__(self, origin, size):
        self.origin = origin
        self.size = size
        extent = self.extent = self.origin + self.size
        super().__init__([
            Point(origin.x, origin.y),
            Point(origin.x, extent.y),
            Point(extent.x, extent.y),
            Point(extent.x, origin.y)
        ])

class Circle(Polygon):
    """
    Approximates a perfect circle with a finite number of line segments:

    >>> circle = Circle(Point.origin, 1, 5)

    """

    def __init__(self, origin, radius, segments):
        self.origin = origin
        self.radius = radius

        angles = (tau * float(a) / segments for a in range(segments))
        super().__init__([
            Point(math.cos(theta) * radius, math.sin(theta) * radius)
            for theta in angles
        ])
