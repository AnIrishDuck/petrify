import math
from petrify.geometry import tau

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
