from ..plane import ComplexPolygon

class Pocket:
    def __init__(self, polygon, depth, start=None):
        assert depth > 0
        self.polygon = polygon
        self.depth = depth
        self.start = start
