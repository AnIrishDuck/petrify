"""
Basic representations of common two-dimensional shapes:

:py:class:`Rectangle` :
    An axis-aligned rectangle.
:py:class:`Circle` :
    A planar circle with a defined origin and radius.

Also contains convenience methods for creating complex polygons:

:py:func:`arc` :
    a semi-circular arc of points
:py:func:`bezier` :
    a bezier curve with specified control points

"""
import math
from geomdl import BSpline
from geomdl import utilities

from .plane import Polygon, Point, Vector
from .geometry import tau
from .machine.util import frange

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

def bezier(a, b, c, d, segments=10):
    """
    Creates a bezier curve between the given control points, approximated with
    a given number of `segments`:

    >>> points = bezier(Point(0, 0), Point(5, 0), Point(5, 5), Point(10, 5), 4)
    >>> [p.snap(1.0) for p in points]
    [Point(0.0, 0.0), Point(4.0, 1.0), Point(6.0, 4.0), Point(10.0, 5.0)]

    """
    r = BSpline.Curve()

    # Set up the Bezier curve
    r.degree = 3
    r.ctrlpts = [p.xy for p in (a, b, c, d)]

    # Auto-generate knot vector
    r.knotvector = utilities.generate_knot_vector(r.degree, len(r.ctrlpts))

    # Set evaluation delta
    r.sample_size = segments

    # Evaluate curve
    r.evaluate()
    return [Point(*xy) for xy in r.evalpts]

def arc(center, radius, start, end, segments=10):
    """
    Creates an arc of points around the given `center` with a specified `radius`
    and `start` and `end` angles, approximated with a fixed number of `segments`:

    >>> points = arc(Point(5, 0), 5, 0, tau / 2, segments = 3)
    >>> [p.snap(0.1) for p in points]
    [Point(10.0, 0.0), Point(5.0, 5.0), Point(0.0, 0.0)]

    """
    angles = frange(start, end, (end - start) / (segments - 1), inclusive=True)
    return [Point(math.cos(theta), math.sin(theta)) * radius + Vector(*center.xy)
            for theta in angles]
