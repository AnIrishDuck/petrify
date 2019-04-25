from ..plane import Line, LineSegment, Point, Vector

class PlanarToolpath:
    """
    Planar toolpaths are continuous movements of the tool that require no
    clearance.

    """
    def __init__(self, start):
        self.path = [start]

    def move_to(self, p):
        self.path.append(p)

    def segments(self):
        return [LineSegment(a, b) for a, b in zip(self.path, self.path[1:])]

    @property
    def current(self):
        return self.path[-1]

class Motion:
    def __init__(self, x=None, y=None, z=None, f=None):
        self.x = x
        self.y = y
        self.z = z
        self.f = f

    def __repr__(self):
        return "Motion(x={0.x}, y={0.y}, z={0.z}, f={0.f})".format(self)

    @property
    def xyz(self): return [self.x, self.y, self.z]

    def merge(self, other):
        return Motion(
            x=other.x or self.x,
            y=other.y or self.y,
            z=other.z or self.z,
            f=other.f or self.f
        )

    def gcode(self):
        assert(self.f is not None)
        parts = ['G01']
        if self.x: parts.append('X{0}'.format(self.x))
        if self.y: parts.append('Y{0}'.format(self.y))
        if self.z: parts.append('Z{0}'.format(self.z))
        parts.append('F{0}'.format(self.f))
        return parts.join(' ')

class Cut:
    def named(self, name):
        return NamedPhase(name, self)

    def then(self, other):
        return Sequence([self, other])

    def gcode(self, f):
        for parent, motion in self.motions():
            f.write(motion.gcode())

    def visualize(self, colors={}):
        import pythreejs as js
        import numpy as np

        prior = Motion(x=0, y=0, z=0, f=0)
        lines = []
        line_colors = []

        for parent, motion in self.motions():
            updated = prior.merge(motion)
            lines.extend([prior.xyz, updated.xyz])
            prior = updated
            color = [0, 1, 0]
            line_colors.extend([color, color])

        lines = np.array(lines, dtype=np.float32)
        line_colors = np.array(line_colors, dtype=np.float32)
        geometry = js.BufferGeometry(
            attributes={
                'position': js.BufferAttribute(lines, normalized=False),
                'color': js.BufferAttribute(line_colors, normalized=False),
            },
        )
        material = js.LineBasicMaterial(vertexColors='VertexColors', linewidth=1)
        return js.LineSegments(geometry, material)

class NamedPhase(Cut):
    def __init__(self, name, inner):
        self.name = name
        self.inner = inner

    def motions(self):
        return self.inner.motions()

class CutSteps(Cut):
    def __init__(self, passes, steps, configuration):
        self.passes = passes
        self.steps = steps
        self.configuration = configuration

    def motions(self):
        m = self.configuration.machine
        s = self.configuration.speeds

        for step in self.steps:
            for p in self.passes:
                path = p.path
                yield (self, Motion(z=m.clearance, f=s.z))
                yield (self, Motion(x=path[0].x, y=path[0].y, f=s.xy))
                yield (self, Motion(z=step, f=s.z))
                for point in path[1:]:
                    yield (self, Motion(x=point.x, y=point.y, f=s.xy))

class Batch(Cut):
    def __init__(self, phases):
        self.phases = phases

    def then(self, other):
        return Sequence([*self.phases, other])

    def motions(self):
        for phase in self.phases:
            for parent, motion in phase.motions():
                yield (parent, motion)
