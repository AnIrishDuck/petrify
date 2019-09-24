.. image:: logo.png
    :target: https://mybinder.org/v2/gh/anirishduck/petrify/master?filepath=examples/logo.ipynb
    :alt: Petrify Logo

.. image:: https://travis-ci.org/AnIrishDuck/petrify.svg?branch=master
    :target: https://travis-ci.org/AnIrishDuck/petrify

.. image:: https://readthedocs.org/projects/petrify/badge/?version=latest
    :target: https://petrify.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/gh/anirishduck/petrify/master?filepath=examples/solids.ipynb

A library for constructing, importing, visualizing, modifying, and exporting
three-dimensional geometry and toolpaths. Designed for CAD / CAM applications.

To get started with this library, we recommend walking through the demos below.
Each notebook contains links to our comprehensive class and method-level
documentation_.

.. _documentation: https://petrify.readthedocs.io/en/latest/?badge=latest

Online Demo
-----------

Thanks to the magic of binder_, you can try out petrify online. We have demos
for several core petrify features:

- Construction of many basic solids_.
- Methods for defining advanced_ solids.
- Combining_ multiple solids into a single complex solid.
- Setting visual_ properties on solids to create the above logo.

Have patience; notebooks on binder can take up to a minute to start. Due to a
(possible) bug in pythreejs, you'll need to click "restart and run all" to see
the relevant interactive visualizations.

.. _binder: https://mybinder.org
.. _solids: https://mybinder.org/v2/gh/anirishduck/petrify/master?filepath=examples/solids.ipynb
.. _advanced: https://mybinder.org/v2/gh/anirishduck/petrify/master?filepath=examples/advanced.ipynb
.. _Combining: https://mybinder.org/v2/gh/anirishduck/petrify/master?filepath=examples/csg.ipynb
.. _visual: https://mybinder.org/v2/gh/anirishduck/petrify/master?filepath=examples/logo.ipynb

Design Principles
-----------------

- **Novice focus**. This library should make it as easy as possible to build
  and manipulate solids, shapes, and other geometry.
- **Immutable operation**. Immutable math is easier for most audiences to reason
  about. This library explicitly does not target strong real-time applications
  like games that demand mutability for performance.
- **Pluggable engines**. CSG is complicated. Different engines have different
  tradeoffs:

  - The pymesh engine is the default where the pymesh2_ library is installed. It
    uses the CGAL CSG engine, which is mature and quite fast. However, building
    pymesh with CGAL support can be difficult for novices and in certain
    environments (like Windows and OSX).
  - cython-csg is relatively fast, but still requires a cython build toolchain.
  - pycsg is a pure-python implementation. It is obviously quite slow, but works
    everywhere python does. For example, pure python environments like pyiodide_
    can utilize this engine easily.

.. _pymesh2: https://pypi.org/project/pymesh2/
.. _pyiodide: https://github.com/iodide-project/pyodide

Quickstart with Docker
----------------------

We recommend using petrify inside our prepackaged docker_ image. This image
has all the necessary libraries for running a Jupyter notebook server, and the
pymesh engine already installed::

  docker run -it -p 8888:8888 \
    -v $(pwd)/notebooks:/home/jovyan/work \
    anirishduck/petrify

The above command will expose a notebook on port 8888 with the necessary volume
mounts for persisting the `work` directory. The server will output a
:code:`?token=<xxxxx>` query parameter you will need for authentication.

.. _docker: https://docker.com

Installation
------------

petrify is published online via pip::

  pip install petrify

We strongly recommend using its visualization capabilities in combination with
Jupyter_::

  pip install notebook pythreejs

While petrify is functional from this point, you almost certainly want to
install a more powerful engine than the default pycsg one. See our csg_ example
for more detail on why; read on to learn how.

.. _Jupyter: https://jupyter.org/
.. _csg: https://github.com/AnIrishDuck/petrify/blob/master/examples/csg.ipynb

pymesh2
=======

pymesh is the most mature driver, but also has the most complicated installation
procedure. We currently only recommend this installation in a Linux-like
environment. You can also use WSL_ if on Windows, or a VM on OSX.

You will need to build pymesh with CGAL_ support to use this engine. To install
in Ubuntu or Debian environments::

  sudo apt-get install libcgal-dev

Now, you can install using the normal PyMesh installation procedure_. In
Linux-like environments, you can probably just install all the needed
library dependencies in the documentation, and then run::

  pip install pymesh2

.. _WSL: https://docs.microsoft.com/en-us/windows/wsl/install-win10
.. _CGAL: https://www.cgal.org/
.. _MacPorts: https://www.macports.org/
.. _procedure: https://pymesh.readthedocs.io/en/latest/installation.html

cython-csg
==========

Installation of cython-csg requires a working build of cython, which should be
available on most major platforms::

  pip install cython

From here, the installation of cython-csg should be entirely automated::

  pip install cython-csg

Contributors
------------

This library is a fusion of:

- pycsg
- pyeuclid v3 fork (https://github.com/ezag/pyeuclid/)
- the reverbat STL PR on pycsg (https://github.com/timknip/pycsg/pull/9)
