"""
Basic representations of common two-dimensional shapes:

:py:class:`Rectangle` :
    An axis-aligned rectangle.
:py:class:`Circle` :
    A planar circle with a defined origin and radius.
:py:class:`Text` :
    The shapes formed from a line of text.

Also contains convenience methods for creating complex polygons:

:py:func:`arc` :
    a semi-circular arc of points
:py:func:`bezier` :
    a bezier curve with specified control points
:py:func:`fillet` :
    a filleted corner with a specified radius from three points

"""
import math
from geomdl import BSpline
from geomdl import utilities

from .plane import ComplexPolygon2, Polygon2, Point2, Vector2
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

    def __repr__(self):
        return "Rectangle({0!r}, {1!r})".format(self.origin, self.size)

class Circle(Polygon2):
    """
    Approximates a perfect circle with a finite number of line segments:

    >>> circle = Circle(Point2.origin, 1, 5)

    """

    def __init__(self, origin, radius, segments=10):
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

    You can also use relative :py:class:`~petrify.plane.Vector` controls instead
    of absolute points:

    >>> points = bezier(Point2(0, 0), Vector2(5, 0), Vector2(-5, 0), Point2(10, 5), 4)
    >>> [p.snap(1.0) for p in points]
    [Point2(0.0, 0.0), Point2(4.0, 1.0), Point2(6.0, 4.0), Point2(10.0, 5.0)]

    """

    if b.__class__ == Vector2:
        b = a + b
    if c.__class__ == Vector2:
        c = d + c
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

def fillet(a, b, c, r, segments=10):
    """
    Creates a smooth circular fillet from an ordered triplet of points that
    define a corner:

    >>> points = fillet(Point2(1, 0), Point2(0, 0), Point2(0, 1), 0.5, segments = 3)
    >>> [p.snap(0.1) for p in points]
    [Point2(0.5, 0.0), Point2(0.1, 0.1), Point2(0.0, 0.5)]

    """
    def clock(v):
        return ((-1 if v.y < 0 else 1) * math.acos(v.x / v.magnitude()))

    angle = (b-a).angle(b-c)
    dv = (a-b).normalized()
    sign = -1 if Polygon2([a, b, c]).clockwise() else 1
    dba = (sign * dv).cross()
    dbc = (sign * (b-c)).normalized().cross()

    start = clock(-dba)
    final = start + (sign * (-dba).angle(-dbc))
    center = b + (dv * r / math.tan(angle / 2)) + (dba * r)
    return arc(center, r, start, final, segments)

def character(face, c):
    face.set_char_size(48 * 64)
    face.load_char(c)
    points = [(p[0], p[1]) for p in face.glyph.outline.points]

    start, end = 0, 0

    slot = face.glyph
    outline = slot.outline

    shapes = []
    for i in range(len(outline.contours)):
        end    = outline.contours[i]
        points = outline.points[start:end+1]
        points.append(points[0])
        tags   = outline.tags[start:end+1]
        tags.append(tags[0])

        segments = [ [points[0],], ]
        for j in range(1, len(points) ):
            segments[-1].append(points[j])
            if tags[j] & (1 << 0) and j < (len(points)-1):
                segments.append( [points[j],] )

        verts = [points[0], ]
        for segment in segments:
            points = [Point2(*t) for t in segment]
            if len(segment) == 2:
                verts.extend(segment[1:])
            elif len(segment) == 3:
                verts.extend(bezier(points[0], points[1], points[1], points[2]))#segment[1:])
            elif len(segment) == 4:
                verts.extend(bezier(points[0], points[1], points[2], points[3]))
            else:
                # TODO - curves to join start and end
                verts.append(segment[1])
                for i in range(1,len(segment)-2):
                    A,B = segment[i], segment[i+1]
                    C = ((A[0]+B[0])/2.0, (A[1]+B[1])/2.0)
                    verts.extend(bezier(Point2(*A), Point2(*C), Point2(*C), Point2(*B)))
                verts.append(segment[-1])
        shapes.append(verts)
        start = end+1

    return ComplexPolygon2([Polygon2([Point2(*xy) / (48 * 64) for xy in vs]) for vs in shapes])

class Text(ComplexPolygon2):
    """
    Using a :class:`Face` provided by the freetype-py_ bindings, generate a
    :py:class:`~petrify.plane.ComplexPolygon2` for the corresponding
    text:

    >>> from freetype import Face
    >>> face = Face('./tests/fixtures/RussoOne.ttf')
    >>> polygon = Text(face, 'petrify')

    .. _`freetype-py`: https://pypi.org/project/freetype-py/
    """
    def __init__(self, face, text):
        self.text = text
        face.set_char_size(48 * 64)
        slot = face.glyph

        x, y = 0, 0
        previous = 0
        polygons = []
        for c in text:
            face.load_char(c)
            kerning = face.get_kerning(previous, c)
            x += (kerning.x >> 6)
            polygons.append(character(face, c) + Vector2(x, 0) / 48)
            x += (slot.advance.x >> 6)
            previous = c

        super().__init__(
            interior=[p for c in polygons for p in c.interior],
            exterior=[p for c in polygons for p in c.exterior]
        )
