class Pocket:
    def __init__(self, inside, outside, depth):
        assert depth > 0
        self.outside = outside
        self.inside = inside
        self.depth = depth
