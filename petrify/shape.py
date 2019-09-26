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

from .plane import Polygon2, Point2, Vector2
from .geometry import tau
from .machine.util import frange

class Rectangle(Polygon2):
    """
    An axis-aligned rectangle with a point of `origin` and a vector `size`:

    >>> square = Rectangle(Point2.origin, Vector2(1, 1))

    """

    def __init__(self, origin, size):
        self.origin = origin
        self.size = size
        extent = self.extent = self.origin + self.size
        super().__init__([
            Point2(origin.x, origin.y),
            Point2(origin.x, extent.y),
            Point2(extent.x, extent.y),
            Point2(extent.x, origin.y)
        ])

class Circle(Polygon2):
    """
    Approximates a perfect circle with a finite number of line segments:

    >>> circle = Circle(Point2.origin, 1, 5)

    """

    def __init__(self, origin, radius, segments):
        self.origin = origin
        self.radius = radius

        angles = (tau * float(a) / segments for a in range(segments))
        super().__init__([
            Point2(math.cos(theta) * radius, math.sin(theta) * radius)
            for theta in angles
        ])

def bezier(a, b, c, d, segments=10):
    """
    Creates a bezier curve between the given control points, approximated with
    a given number of `segments`:

    >>> points = bezier(Point2(0, 0), Point2(5, 0), Point2(5, 5), Point2(10, 5), 4)
    >>> [p.snap(1.0) for p in points]
    [Point2(0.0, 0.0), Point2(4.0, 1.0), Point2(6.0, 4.0), Point2(10.0, 5.0)]

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
    return [Point2(*xy) for xy in r.evalpts]

def arc(center, radius, start, end, segments=10):
    """
    Creates an arc of points around the given `center` with a specified `radius`
    and `start` and `end` angles, approximated with a fixed number of `segments`:

    >>> points = arc(Point2(5, 0), 5, 0, tau / 2, segments = 3)
    >>> [p.snap(0.1) for p in points]
    [Point2(10.0, 0.0), Point2(5.0, 5.0), Point2(0.0, 0.0)]

    """
    angles = frange(start, end, (end - start) / (segments - 1), inclusive=True)
    return [Point2(math.cos(theta), math.sin(theta)) * radius + Vector2(*center.xy)
            for theta in angles]
