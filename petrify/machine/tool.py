class Speed:
    def __init__(self, dx, dy, dz):
        self.dx = dx
        self.dy = dy
        self.dz = dz

class StraightTip:
    def __init__(self, diameter):
        self.diameter = diameter

    @property
    def radius(self):
        return self.diameter / 2

class Machine:
    def __init__(self, clearance):
        pass

class Tool:
    def __init__(self, tip, feeds, speeds):
        self.tip = tip
        self.feeds = feeds
        self.speeds = speeds
