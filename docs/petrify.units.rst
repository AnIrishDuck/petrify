Unit Conversions
================

Motivation
----------
 The MCO MIB has determined that the root cause for the loss of the MCO
 spacecraft was the failure to use metric units in the coding of a ground
 software file, “Small Forces,” used in trajectory models. Specifically,
 thruster performance data in English units instead of metric units was used in
 the software application code titled SM_FORCES (small forces). The output from
 the SM_FORCES application code as required by a MSOP Project Software Interface
 Specification (SIS) was to be in metric units of Newtonseconds (N-s). Instead,
 the data was reported in English units of pound-seconds (lbf-s). The Angular
 Momentum Desaturation (AMD) file contained the output data from the SM_FORCES
 software. The SIS, which was not followed, defines both the format and units of
 the AMD file generated by ground-based computers. Subsequent processing of the
 data from AMD file by the navigation software algorithm therefore,
 underestimated the effect on the spacecraft trajectory by a factor of 4.45,
 which is the required conversion factor from force in pounds to Newtons. An
 erroneous trajectory was computed using this incorrect data.

            `Mars Climate Orbiter Mishap Investigation Phase I Report`
            `PDF <ftp://ftp.hq.nasa.gov/pub/pao/reports/1999/MCO_report.pdf>`_

How Petrify Handles Units
-------------------------

Many operations, particularly in CAM, are unit-critical. Complicating this
problem, most external formats do not provide a unit or scale for inputted
geometry. Petrify makes no assumptions about the units implicit in these files.

As such, you must specify all units yourself when reading and writing data. We
use the excellent `pint`_ library for handling these units. A predefined unit
registry is accessible via the `petrify.u` convenience variable:

.. doctest::

    >>> from petrify import u
    >>> from petrify.formats import SVG

You can specify the file scale in one of two ways. First, you can directly
specify the corresponding `pint` unit:

.. doctest::

    >>> paths = SVG.read('../tests/fixtures/example.svg', 'mm')
    >>> paths = SVG.read('../tests/fixtures/example.svg', u.mm)

You can also specify a scale conversion factor, which must use the specially
defined `u.file` unit in the denominator. The following imports a SVG where
90 file units equal one inch (in other words, 90 DPI):

.. doctest::

    >>> paths = SVG.read('../tests/fixtures/example.svg', u.inches / (90 * u.file))

Thanks to the magic of `pint`, all normal operations are functional as long as
you tag the input objects with units:

.. doctest::

    >>> from petrify.solid import Box, Vector, Point
    >>> box = Box(Point.origin, Vector(1, 1, 1)).as_unit(u.mm)
    >>> (box + (Vector.basis.x * u.inch)).envelope().origin
    Point(25.4, 0.0, 0.0)

To prevent constant conversions, you can use an implicit "internal" unit. You
still must always specify your input and output units:

.. testcode::

    from tempfile import NamedTemporaryFile
    from petrify.formats import STL

    data = STL.read('../tests/fixtures/svg.stl', 'mm').m_as('inch')
    data += Box(Point.origin, Vector(1, 1, 1))
    with NamedTemporaryFile() as fp:
        STL(fp.name, 'mm').write(data.as_unit('inch'))


.. _`pint`: https://pint.readthedocs.io/en/0.9/
