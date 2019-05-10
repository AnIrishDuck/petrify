class Engrave:
    def __init__(self, polygon, depth):
        assert depth > 0
        self.polygon = polygon
        self.depth = depth
