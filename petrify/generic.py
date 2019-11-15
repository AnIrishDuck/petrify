from . import plane, space
from .plane import Line2, Point2, Polygon2, Vector2
from .space import Line3, Point3, Polygon3, Vector3

class Point:
    """
    A generic constructor that chooses the correct variant of
    :py:`~petrify.plane.Point2` or :py:`~petrify.space.Point3` based on argument
    count:

    >>> Point(1, 2)
    Point(1, 2)
    >>> Point(1, 2, 3)
    Point(1, 2, 3)

    """

    def __new__(cls, *args):
        if len(args) == 2:
            return Point2(*args)
        elif len(args) == 3:
            return Point3(*args)
        else:
            return Notimplemented
Point.origin = Point3.origin

class Vector:
    """
    A generic constructor that chooses the correct variant of
    :py:`~petrify.plane.Vector` or :py:`~petrify.space.Vector` based on argument
    count:

    >>> Vector(1, 2)
    Vector(1, 2)
    >>> Vector(1, 2, 3)
    Vector(1, 2, 3)

    """

    def __new__(cls, *args):
        if len(args) == 2:
            return Vector2(*args)
        elif len(args) == 3:
            return Vector3(*args)
        else:
            return Notimplemented
Vector.basis = Vector3.basis

def embedding_from(args):
    embeds = list(set(a.embedding for a in args))
    assert (len(embeds) == 1), 'arguments must either be all spatial or all planar'
    return embeds[0]

def create(Klass2, Klass3, e, args):
    if e == plane:
        return Klass2(*args)
    elif e == space:
        return Klass3(*args)
    else:
        return NotImplemented

class Polygon:
    """
    A generic constructor that chooses the correct variant of
    :py:`~petrify.plane.Polygon2` or :py:`~petrify.space.Polygon3` based on
    the embedding of the passed arguments:

    >>> Polygon([Point(0, 0), Point(1, 0), Point(1, 1)])
    Polygon([Point(0, 0), Point(1, 0), Point(1, 1)])
    >>> Polygon([Point(0, 0, 0), Point(1, 0, 0), Point(1, 1, 1)])
    Polygon([Point(0, 0, 0), Point(1, 0, 0), Point(1, 1, 1)])
    >>> Polygon([Point(0, 0), Point(1, 1, 2)])
    Traceback (most recent call last):
    ...
    AssertionError: arguments must either be all spatial or all planar

    """

    def __new__(cls, points):
        return create(Polygon2, Polygon3, embedding_from(points), [points])

class Line:
    """
    A generic constructor that chooses the correct variant of
    :py:`~petrify.plane.Line2` or :py:`~petrify.space.Line3` based on
    the embedding of the passed arguments:

    >>> Line(Point(0, 0), Point(1, 0))
    Line(Point(0, 0), Vector(1, 0))
    >>> Line(Point(0, 0, 0), Point(1, 0, 0))
    Line(Point(0, 0, 0), Vector(1, 0, 0))
    >>> Line(Point(0, 0, 0), Point(1, 0))
    Traceback (most recent call last):
    ...
    AssertionError: arguments must either be all spatial or all planar

    """

    def __new__(cls, *args):
        return create(Line2, Line3, embedding_from(args), args)
