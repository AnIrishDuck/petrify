from .pocket import Pocket
from .part import Part

class Speed:
    def __init__(self, xy, z):
        self.xy = xy
        self.z = z

class StraightTip:
    def __init__(self, diameter):
        self.diameter = diameter

    @property
    def radius(self):
        return self.diameter / 2

class Machine:
    def __init__(self, clearance):
        self.clearance = clearance

    def configure(self, feed, speeds, tool):
        return Configuration(feed, speeds, tool, self)


class Configuration:
    def __init__(self, feed, speeds, tool, machine):
        self.speeds = speeds
        self.feed = feed
        self.tool = tool
        self.machine = machine

    def cut(self, shape):
        if isinstance(shape, Pocket):
            return self.feed.pocket(self, shape)
        elif isinstance(shape, Part):
            return self.feed.part(self, shape)

class Tool:
    def __init__(self, tip, feeds, speeds):
        self.tip = tip
        self.feeds = feeds
        self.speeds = speeds
