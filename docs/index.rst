.. petrify documentation master file, created by
   sphinx-quickstart on Sun Feb 10 20:10:31 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

petrify: a programmatic cad library
===================================

petrify can be used to create open-source programmatic and parametric
three-dimensional models.

Example usage::

  from petrify.solid import Point, Vector, Box

  big = Box(Point(0, 0, 0), Vector(1, 1, 1))
  small = Box(Point(0.5, 0.5, 0.5), Vector(0.5, 0.5, 0.5))
  (big - small).to_stl('example.stl')

Contents
========

.. toctree::
   :maxdepth: 2

   petrify.solid
   petrify.edge
   petrify.space
   petrify.conversions

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
