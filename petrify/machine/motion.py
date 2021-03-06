from ..geometry import tau
from ..generic import Point
from ..plane import Line, LineSegment, Vector
from .. import visualize

class Toolpath:
    def __init__(self, motion, basis, z):
        self.motion = motion
        self.basis = basis
        self.z = z

    def project(self, motion):
        p = self.basis.project(Point(motion.x, motion.y))
        return p + (motion.z * self.z)

    def _lines(self):
        from ..generic import Point, Vector, LineSegment
        import pythreejs as js
        import numpy as np

        prior = Motion(x=0, y=0, z=0, f=0)

        for parent, command in self.motion.commands():
            if isinstance(command, Motion):
                updated = prior.merge(command)
                pv = self.project(prior)
                uv = self.project(updated)
                delta = pv - uv
                start = (uv + pv) / 2
                color = getattr(parent, 'color', [0, 1, 0])
                yield (LineSegment(pv, uv), color)
                prior = updated

    @property
    def points(self):
        return [p for l, c in self._lines() for p in (l.p1, l.p2)]

    def mesh(self):
        return visualize.segments(self._lines())

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

    def __add__(self, v):
        if not isinstance(v, Vector):
            return NotImplemented
        return self.merge(
            Motion(
                x=(self.x + v.x if self.x is not None else None),
                y=(self.y + v.y if self.y is not None else None),
            )
        )

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
        return ' '.join(parts)

class Cut:
    def props(self, **props):
        return AnnotatedPhase(self, props)

    def then(self, other):
        return Sequence([self, other])

    def gcode(self, f):
        for parent, command in self.commands():
            f.write(command.gcode())
            f.write('\n')

    def time(self):
        state = Motion(0, 0, 0, 0)
        dt = 0
        for (parent, cmd) in self.commands():
            if isinstance(cmd, Motion):
                prior = Point(state.x, state.y, state.z)
                state = state.merge(cmd)
                fr = state.f
                cur = Point(state.x, state.y, state.z)
                d = (cur - prior).magnitude()
                dt += (d / fr)

        return dt

    def visualize(self, colors={}):
        from ..space import Vector
        import pythreejs as js
        import numpy as np

        prior = Motion(x=0, y=0, z=0, f=0)
        lines = []
        line_colors = []

        for parent, command in self.commands():
            if isinstance(command, Motion):
                updated = prior.merge(command)
                pv = Vector(*prior.xyz)
                uv = Vector(*updated.xyz)
                delta = pv - uv
                start = (uv + pv) / 2
                lines.extend([prior.xyz, updated.xyz])
                a1 = delta.rotate(Vector(0, 0, 1), tau / 16) * 0.1
                a2 = delta.rotate(Vector(0, 0, 1), -tau / 16) * 0.1
                lines.extend([start, (a1 + start).xyz, start, (a2 + start).xyz])
                prior = updated
                color = getattr(parent, 'color', [0, 1, 0])
                line_colors.extend([color, color])
                line_colors.extend([color, color])
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

class AnnotatedPhase(Cut):
    def __init__(self, inner, props):
        self.inner = inner
        for key, prop in props.items():
            setattr(self, key, prop)

    def commands(self):
        return ((self, command) for _, command in self.inner.commands())

class CutSteps(Cut):
    def __init__(self, passes, steps, configuration):
        self.passes = passes
        self.steps = steps
        self.configuration = configuration

    def commands(self):
        m = self.configuration.machine
        s = self.configuration.speeds.to(m.format)

        clearance = m.clearance.m_as(self.configuration.units)

        for step in self.steps:
            for p in self.passes:
                path = p.path
                yield (self, Motion(z=clearance, f=s.z))
                yield (self, Motion(x=path[0].x, y=path[0].y, f=s.xy))
                yield (self, Motion(z=step, f=s.z))
                for point in path[1:]:
                    yield (self, Motion(x=point.x, y=point.y, f=s.xy))
                yield (self, Motion(z=clearance, f=s.z))

class Batch(Cut):
    def __init__(self, phases):
        self.phases = phases

    def __add__(self, v):
        if not isinstance(v, Vector):
            return NotImplemented
        return MovedBatch(self.phases, v)

    def then(self, other):
        return Batch([*self.phases, other])

    def commands(self):
        for phase in self.phases:
            for parent, command in phase.commands():
                yield (parent, command)

class MovedBatch(Batch):
    def __init__(self, phases, translate):
        super().__init__(phases)
        self.translate = translate

    def commands(self):
        for phase in self.phases:
            for parent, command in phase.commands():
                yield (parent, command + self.translate)
