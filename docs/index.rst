.. petrify documentation master file, created by
   sphinx-quickstart on Sun Feb 10 20:10:31 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to petrify's documentation!
===================================

petrify can be used to create programmatic / parametric three-dimensional models.

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

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
