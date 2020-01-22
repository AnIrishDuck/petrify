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
        from .plane import Vector2
        from .space import Vector3
        if len(args) == 2:
            return Vector2(*args)
        elif len(args) == 3:
            return Vector3(*args)
        else:
            return NotImplemented

class Point(Vector):
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
        from .plane import Point2
        from .space import Point3
        if len(args) == 2:
            return Point2(*args)
        elif len(args) == 3:
            return Point3(*args)
        else:
            return NotImplemented

def embedding_from(args):
    embeds = list(set(a.embedding for a in args))
    assert (len(embeds) == 1), 'arguments must either be all spatial or all planar'
    return embeds[0]

def create(Klass2, Klass3, e, args):
    from . import plane, space
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
        from .plane import Polygon2
        from .space import Polygon3
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
        from .plane import Line2
        from .space import Line3
        return create(Line2, Line3, embedding_from(args), args)

class Ray:
    """
    A generic constructor that chooses the correct variant of
    :py:`~petrify.plane.Ray2` or :py:`~petrify.space.Ray3` based on
    the embedding of the passed arguments:

    >>> Ray(Point(0, 0), Vector(1, 0))
    Ray(Point(0, 0), Vector(1, 0))
    >>> Ray(Point(0, 0, 0), Vector(1, 0, 0))
    Ray(Point(0, 0, 0), Vector(1, 0, 0))
    >>> Ray(Point(0, 0, 0), Point(1, 0))
    Traceback (most recent call last):
    ...
    AssertionError: arguments must either be all spatial or all planar

    """

    def __new__(cls, *args):
        from .plane import Ray2
        from .space import Ray3
        return create(Ray2, Ray3, embedding_from(args), args)

class LineSegment:
    """
    A generic constructor that chooses the correct variant of
    :py:`~petrify.plane.LineSegment2` or :py:`~petrify.space.LineSegment3` based
    on the embedding of the passed arguments:

    >>> LineSegment(Point(0, 0), Point(1, 0))
    LineSegment(Point(0, 0), Point(1, 0))
    >>> LineSegment(Point(0, 0, 0), Point(1, 0, 0))
    LineSegment(Point(0, 0, 0), Point(1, 0, 0))
    >>> LineSegment(Point(0, 0, 0), Point(1, 0))
    Traceback (most recent call last):
    ...
    AssertionError: arguments must either be all spatial or all planar

    """

    def __new__(cls, *args):
        from .plane import LineSegment2
        from .space import LineSegment3
        return create(LineSegment2, LineSegment3, embedding_from(args), args)
