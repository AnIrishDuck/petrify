=======
Petrify
=======

.. image:: https://travis-ci.org/AnIrishDuck/petrify.svg?branch=master
    :target: https://travis-ci.org/AnIrishDuck/petrify

.. image:: https://readthedocs.org/projects/petrify/badge/?version=latest
    :target: https://petrify.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

A library for working with three-dimensional geometry. Designed for CAD / CAM
applications.

Design Principles
-----------------

- **Novice focus**. This library should make it as easy as possible to build
  and manipulate solids, shapes, and other geometry.
- **Immutable operation**. Immutable math is easier for novices to reason about.
  This library explicitly does not target strong real-time applications like
  games that demands mutability for performance.
- **Pluggable engines**. CSG is complicated. Different engines have different
  tradeoffs:

  - The pymesh engine is the default where the pymesh2_ library is installed. It
    uses the IGL engine, which is mature and quite fast. However, building
    pymesh with IGL support can be difficult for novices and in certain
    environments (like Windows).
  - cython-csg is relatively fast, but still requires a cython build toolchain.
  - pycsg is a pure-python implementation. It is obviously quite slow, but works
    everywhere python does. For example, pure python environments like pyiodide_
    can utilize this engine easily.

.. _pymesh2: https://pypi.org/project/pymesh2/
.. _pyiodide: https://github.com/iodide-project/pyodide

Contributors
------------

This library is a fusion of:

- pycsg
- pyeuclid v3 fork (https://github.com/ezag/pyeuclid/)
- the reverbat STL PR on pycsg (https://github.com/timknip/pycsg/pull/9)
