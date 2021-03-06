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
from .generic import Point, Vector
from .geometry import tau
from .util import frange

def assert_type(v, name, options):
    if isinstance(options, list):
        type = "one of {0}".format(', '.join(o.__name__ for o in options))
    else:
        type = str(options)
        options = [options]
    msg = "{0} must be {1}".format(name, type)
    assert any(isinstance(v, t) for t in options), msg


class Rectangle(Polygon2):
    """
    An axis-aligned rectangle with a point of `origin` and a vector or point
    `extent`:

    >>> Rectangle(Point(0, 0), Vector(1, 1))
    Rectangle(Point(0, 0), Vector(1, 1))
    >>> Rectangle(Point(1, 1), Point(2, 3))
    Rectangle(Point(1, 1), Vector(1, 2))

    """

    def __init__(self, origin, extent):
        assert_type(origin, 'origin', Point2)
        self.origin = origin

        assert_type(extent, 'extent', [Point2, Vector2])
        if isinstance(extent, Point2):
            self.extent = extent
            self.size = self.extent - self.origin
        else:
            self.size = extent
            extent = self.extent = self.origin + self.size

        super().__init__([
            Point(origin.x, origin.y),
            Point(origin.x, extent.y),
            Point(extent.x, extent.y),
            Point(extent.x, origin.y)
        ])

    def __repr__(self):
        return "Rectangle({0!r}, {1!r})".format(self.origin, self.size)

class Circle(Polygon2):
    """
    Approximates a perfect circle with a finite number of line segments:

    >>> circle = Circle(Point(0, 0), 1, 5)

    """

    def __init__(self, origin, radius, segments=10):
        self.origin = origin
        self.radius = radius

        angles = (tau * float(a) / segments for a in range(segments))
        super().__init__([
            self.origin + Vector(math.cos(theta) * radius, math.sin(theta) * radius)
            for theta in angles
        ])

def bezier(a, b, c, d, segments=10):
    """
    Creates a bezier curve between the given control points, approximated with
    a given number of `segments`:

    >>> points = bezier(Point(0, 0), Point(5, 0), Point(5, 5), Point(10, 5), 4)
    >>> [p.snap(1.0) for p in points]
    [Point(0.0, 0.0), Point(4.0, 1.0), Point(6.0, 4.0), Point(10.0, 5.0)]

    You can also use relative :py:class:`~petrify.plane.Vector` controls instead
    of absolute points:

    >>> points = bezier(Point(0, 0), Vector(5, 0), Vector(-5, 0), Point(10, 5), 4)
    >>> [p.snap(1.0) for p in points]
    [Point(0.0, 0.0), Point(4.0, 1.0), Point(6.0, 4.0), Point(10.0, 5.0)]

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

def fillet(a, b, c, r, segments=10):
    """
    Creates a smooth circular fillet from an ordered triplet of points that
    define a corner:

    >>> points = fillet(Point(1, 0), Point(0, 0), Point(0, 1), 0.5, segments = 3)
    >>> [p.snap(0.1) for p in points]
    [Point(0.5, 0.0), Point(0.1, 0.1), Point(0.0, 0.5)]

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
            points = [Point(*t) for t in segment]
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
                    verts.extend(bezier(Point(*A), Point(*C), Point(*C), Point(*B)))
                verts.append(segment[-1])
        shapes.append(verts)
        start = end+1

    return ComplexPolygon2([Polygon2([Point(*xy) / (48 * 64) for xy in vs]) for vs in shapes])

class Text(ComplexPolygon2):
    """
    Using a :class:`Face` provided by the freetype-py_ bindings, generate a
    :py:class:`~petrify.plane.ComplexPolygon2` for the corresponding
    text:

    >>> from freetype import Face
    >>> face = Face('./tests/fixtures/RussoOne.ttf')
    >>> polygon = Text(face, 'petrify')

    Uses the face's pre-defined line height for the size of the text, scaled to
    1.0 units on the y axis.

    .. _`freetype-py`: https://pypi.org/project/freetype-py/
    """
    def __init__(self, face, text):
        self.text = text
        face.set_char_size(48 * 64)
        slot = face.glyph
        scale = float(face.size.height) / (48 * 64)

        x, y = 0, 0
        previous = 0
        polygons = []
        for c in text:
            face.load_char(c)
            kerning = face.get_kerning(previous, c)
            x += (kerning.x >> 6)
            polygons.append((character(face, c) + Vector(x, 0) / 48) * (1.0 / scale))
            x += (slot.advance.x >> 6)
            previous = c

        super().__init__(
            interior=[p for c in polygons for p in c.interior],
            exterior=[p for c in polygons for p in c.exterior]
        )
