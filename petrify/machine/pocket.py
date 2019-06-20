from ..plane import ComplexPolygon
from ..geometry import valid_scalar

class Pocket:
    def __init__(self, polygon, depth, start=None):
        assert depth > 0
        self.polygon = polygon
        self.depth = depth
        self.start = start or 0

    def __mul__(self, v):
        if not valid_scalar(v): return NotImplemented
        return Pocket(self.polygon * v, self.depth * v, self.start * v)
    __rmul__ = __mul__
