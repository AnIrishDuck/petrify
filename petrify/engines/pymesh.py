from ..space import Point, Polygon

import pymesh
import numpy as np

def triangulate(size):
    for a, b in zip(range(1, size), range(2, size)):
        yield (0, a, b)

def facet(polygons):
    ix = 0
    for polygon in polygons:
        count = len(polygon.points)
        for a, b, c in triangulate(count):
            yield [a + ix, b + ix, c + ix]
        ix += count

def from_pymesh(_mesh):
    polygons = []
    for face in _mesh.faces:
        polygons.append(Polygon([Point(*_mesh.vertices[i]) for i in face]))
    return polygons

def to_pymesh(polygons):
    vertices = np.array([p.xyz for polygon in polygons for p in polygon.points])
    faces = np.array(list(facet(polygons)))
    return pymesh.form_mesh(vertices, faces)

def union(*solids):
    def u(a, b):
        return pymesh.boolean(a, b, operation='union', engine='igl')
    whole = to_pymesh(solids[0])
    for polygons in solids[1:]:
        whole = u(whole, to_pymesh(polygons))
    return from_pymesh(whole)

def intersect(a, b):
    mesh = pymesh.boolean(to_pymesh(a), to_pymesh(b),
                          operation='intersection', engine='igl')
    return from_pymesh(mesh)

def subtract(a, b):
    mesh = pymesh.boolean(to_pymesh(a), to_pymesh(b),
                          operation='difference', engine='igl')
    return from_pymesh(mesh)
