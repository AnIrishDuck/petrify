global csg

from . import pycsg
csg = pycsg
enabled = [pycsg]

try:
    from . import cython_csg
    csg = cython_csg
    enabled.append(cython_csg)
except ImportError:
    pass

try:
    from . import pymesh
    csg = pymesh
    enabled.append(pymesh)
except ImportError:
    pass
