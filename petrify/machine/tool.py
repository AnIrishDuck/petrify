from .engrave import Engrave
from .pocket import Pocket
from .part import Part
from ..geometry import valid_scalar
from .. import units

class Format:
    """
    Describes machine `xy` and `z` feedrate units:

    >>> from petrify import u
    >>> format = Format(u.mm / u.second, u.mm / u.second)

    """
    def __init__(self, us, xy = None, z = None, v = None):
        self.units = units.assert_lengthy(1 * us).units
        self.xy = units.assert_speedy(1 * (v or xy)).units
        self.z = units.assert_speedy(1 * (v or z)).units

class StraightTip:
    """
    Specifies a generic straight-tip cutting tool with the specified `number`
    and `diameter`:

    >>> tool = StraightTip(1, 1 / 8) * u.inch

    """
    def __init__(self, number, diameter, name=None):
        self.number = number
        self.diameter = diameter
        self.name = name or '{0} straight'.format(diameter)

    def __mul__(self, v):
        if not valid_scalar(v): return NotImplemented
        return StraightTip(self.number, self.diameter * v, self.name)
    __rmul__ = __mul__

    @property
    def radius(self):
        return self.diameter / 2

class Machine:
    """
    Defines a machine with a given clearance plane that can be configured to
    cut with various tools.

    A machine configuration is obtained via `.configure` and can be used to
    cut out shapes.

    """
    def __init__(self, clearance, format):
        self.clearance = clearance
        self.format = format

    def configure(self, feed, speeds, tool):
        return Configuration(feed, speeds, tool, self)


class Configuration:
    def __init__(self, feed, speeds, tool, machine):
        self.speeds = speeds
        self.feed = feed
        self._tool = units.assert_lengthy(tool)
        self.machine = machine

    @property
    def units(self):
        return self.machine.format.units

    @property
    def tool(self):
        return self._tool.m_as(self.units)

    def cut(self, shape):
        shape = shape.m_as(self.machine.units)
        if isinstance(shape, Pocket):
            return self.feed.pocket(self, shape)
        elif isinstance(shape, Part):
            return self.feed.part(self, shape)
        elif isinstance(shape, Engrave):
            return self.feed.engrave(self, shape)
