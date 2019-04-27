from ..plane import ComplexPolygon

class Pocket:
    def __init__(self, polygon, depth, start=None):
        assert depth > 0
        self.polygon = polygon
        if isinstance(self.polygon, ComplexPolygon):
            self.interior = polygon.interior
            self.exterior = polygon.exterior
        else:
            self.interior = []
            self.exterior = [polygon]
        self.depth = depth
        self.start = start
