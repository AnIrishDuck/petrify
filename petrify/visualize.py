from petrify.geometry import tau

def scene(nodes):
    import pythreejs as js
    from .space import _pmap, Point

    points = [p for n in nodes for p in n.points]
    center = _pmap(Point, sum, points) / len(points)
    end = _pmap(Point, max, points)
    viewline = end - center
    position = center + viewline * 3
    meshes = (n.mesh() for n in nodes)

    light = js.DirectionalLight(color='white', position=[3, 5, 1], intensity=0.5)
    c = js.PerspectiveCamera(
        position=position.xyz,
        up=[0, 1, 0],
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
        controls=[controller]
    )

    return renderer
