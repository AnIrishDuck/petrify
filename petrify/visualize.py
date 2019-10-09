import math
from petrify.geometry import tau

def aspect(properties):
    renderer = properties.get('renderer')
    return renderer['width'] / renderer['height'] if renderer is not None else 1

def scene(nodes, **properties):
    import pythreejs as js
    from .space import _pmap, Point, Vector

    camera_properties = properties.get('camera', {})

    points = [p for n in nodes for p in n.points]
    start = _pmap(Point, min, points)
    end = _pmap(Point, max, points)
    center = camera_properties.get('center', (start + end) / 2)

    # This math shamelessly stolen from:
    # https://github.com/jupyter-widgets/pythreejs/blob/master/js/src/_base/utils.js
    fov = 50
    r2 = max((point - center).magnitude_squared() for point in points)
    delta = (1.5 * math.sqrt(r2)) / math.tan(0.5 * fov * math.pi / 180)
    delta *= Vector(-1, -1, 1).normalized()
    position = camera_properties.get('position', center + delta)
    meshes = (n.mesh() for n in nodes)

    light = js.DirectionalLight(color='white', position=[3, 5, 1], intensity=0.5)
    c = js.PerspectiveCamera(
        aspect=aspect(properties),
        position=position.xyz,
        up=[0, 0, 1],
        children=[light]
    )

    scene = js.Scene(
        children=[*meshes, c, js.AmbientLight(color='#777777')],
        background=None
    )

    controller = js.OrbitControls(controlling=c)
    c.lookAt(center.xyz)
    controller.target = tuple(center.xyz)
    renderer = js.Renderer(
        camera=c,
        scene=scene,
        controls=[controller],
        **properties.get('renderer', {})
    )

    return renderer

def segments(segments, line_width=1):
    import pythreejs as js
    import numpy as np

    lines = []
    line_colors = []

    for (segment, color) in segments:
        lines.append([segment.p1, segment.p2])
        line_colors.append([color, color])

    lines = np.array(lines, dtype=np.float32)
    line_colors = np.array(line_colors, dtype=np.float32)
    geometry = js.LineSegmentsGeometry(
        positions=lines,
        colors=line_colors
    )
    material = js.LineMaterial(vertexColors='VertexColors', linewidth=line_width)
    return js.LineSegments2(geometry, material)

class Grid:
    def __init__(self, basis, ticks, count):
        self.basis = basis
        self.ticks = sorted(ticks)
        self.count = count

    @property
    def points(self):
        return []

    def mesh(self):
        from petrify.space import LineSegment, Point

        count = self.count
        origin = self.basis.origin

        top = self.ticks[-1]

        def halfgrid(c, s, ticks):
            return (
                LineSegment(
                    origin + (c * -count * top) + s * ix,
                    origin + (c * count * top) + s * ix
                )
                for ix in range(-ticks, ticks + 1)
            )

        def grid(t):
            return (
                *halfgrid(self.basis.bx, self.basis.by * t, int(count * (top / t))),
                *halfgrid(self.basis.by, self.basis.bx * t, int(count * (top / t)))
            )

        n = self.basis.bx.cross(self.basis.by)


        def parts(t):
            zs = (n * ix * t for ix in range(0, int(count * (top / t)) + 1))
            axis = (
                LineSegment(
                    Point(*(z - (self.basis.bx * 0.1))),
                    Point(*(z + (self.basis.bx * 0.1)))
                ) for z in zs
            )
            return (*axis, *grid(t))

        def decay():
            v = 0.5
            while True:
                yield v
                v = v / 2

        def all_grid():
            for (tick, color) in reversed(list(zip(reversed(self.ticks), decay()))):
                for l in parts(tick):
                    yield (l, [color, color, color])

        parts = (
            (LineSegment(origin, origin + (n * count)), [0.5, 0.5, 0.5]),
            *all_grid()
        )

        return segments(parts)
