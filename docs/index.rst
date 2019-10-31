.. petrify documentation master file, created by
   sphinx-quickstart on Sun Feb 10 20:10:31 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

petrify: a programmatic cad library
===================================

petrify can be used to create open-source programmatic and parametric
three-dimensional models.

Example usage:

.. testcode::

    from petrify import u, Point, Vector
    from petrify.formats import STL
    from petrify.solid import Box

    big = Box(Point(0, 0, 0), Vector(1, 1, 1))
    small = Box(Point(0.5, 0.5, 0.5), Vector(0.5, 0.5, 0.5))

    STL('example.stl', 'mm').write((big - small).as_unit('in'))

Generics
--------

Object creation often requires switching between 2D and 3D descriptions. For
that reason, we encourage you to use the :class:`Point`, :class:`Vector`, and
:class:`Polygon` definitions exported from the top-level :mod:`petrify`
package.

These objects automatically construct the "correct" representation from
:mod:`petrify.space` or :mod:`petrify.plane` in context:

.. doctest::

    >>> from petrify import Point, Vector, Polygon
    >>> Point(1, 2, 3)
    Point(1, 2, 3)
    >>> Vector(1, 2)
    Vector(1, 2)
    >>> Polygon([Point(0, 0), Point(2, 0), Point(1, 1)])
    Polygon([Point(0, 0), Point(2, 0), Point(1, 1)])
    >>> Polygon([Point(0, 0, 0), Point(2, 0, 1), Point(1, 1, -1)])
    Polygon([Point(0, 0, 0), Point(2, 0, 1), Point(1, 1, -1)])

Contents
========

.. toctree::
   :maxdepth: 2

   petrify.units
   petrify.solid
   petrify.formats
   petrify.shape
   petrify.edge
   petrify.space
   petrify.plane

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
