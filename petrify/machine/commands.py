from ..plane import Vector

class GCode:
    def __init__(self, line):
        self.line = line

    def __add__(self, v):
        if not isinstance(v, Vector):
            return NotImplemented
        return self

    def gcode(self):
        return self.line

class ToolChange:
    def __init__(self, tool):
        self.tool = tool

    def commands(self):
        return [(self, GCode('M6 T{0}'.format(self.tool.number)))]

class Pause:
    def __init__(self, message):
        self.message = message

    def commands(self):
        return [(self, GCode('M0 {0}'.format(self.message)))]

class ToolPause(Pause):
    def __init__(self, tool):
        super().__init__('Tool to {0}'.format(tool.number))
