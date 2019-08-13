from ..geometry import valid_scalar

class Engrave:
    def __init__(self, polygon, depth):
        assert depth > 0
        self.polygon = polygon
        self.depth = depth

    def __mul__(self, v):
        if not valid_scalar(v): return NotImplemented
        return Engrave(self.polygon * v, self.depth * v)
    __rmul__ = __mul__
