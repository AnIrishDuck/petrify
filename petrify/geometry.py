# Geometry
# Much maths thanks to Paul Bourke, http://astronomy.swin.edu.au/~pbourke
# ---------------------------------------------------------------------------
import math
import numbers

tau = math.pi * 2

def valid_scalar(v):
    """
    Checks if `v` is a valid scalar value for the purposes of this library:

    >>> valid_scalar(1)
    True
    >>> valid_scalar(1.0)
    True
    >>> valid_scalar('abc')
    False

    """
    return isinstance(v, numbers.Number)

class Geometry:
    def _connect_unimplemented(self, other):
        raise AttributeError('Cannot connect %s to %s' %
                             (self.__class__, other.__class__))

    def _intersect_unimplemented(self, other):
        raise AttributeError('Cannot intersect %s and %s' %
                             (self.__class__, other.__class__))

    _intersect_point2 = _intersect_unimplemented
    _intersect_line2 = _intersect_unimplemented
    _intersect_circle = _intersect_unimplemented
    _connect_point2 = _connect_unimplemented
    _connect_line2 = _connect_unimplemented
    _connect_circle = _connect_unimplemented

    _intersect_point3 = _intersect_unimplemented
    _intersect_line3 = _intersect_unimplemented
    _intersect_sphere = _intersect_unimplemented
    _intersect_plane = _intersect_unimplemented
    _connect_point3 = _connect_unimplemented
    _connect_line3 = _connect_unimplemented
    _connect_sphere = _connect_unimplemented
    _connect_plane = _connect_unimplemented

    def intersect(self, other):
        raise NotImplementedError

    def connect(self, other):
        raise NotImplementedError

    def distance(self, other):
        c = self.connect(other)
        if c:
            return c.length
        return 0.0
