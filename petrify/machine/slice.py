from ..solid import PlanarPolygon, PolygonExtrusion
from ..space import Plane
from ..plane import ComplexPolygon
from ..util import frange

from .. import decompose, geometry

class Sliced:
    def __init__(self, solid, basis, rectangle, start, end, step):
        self.solid = solid
        self.basis = basis
        self.slice = rectangle

        self.start = start
        self.end = end
        self.step = step

        r = frange(self.start, self.end, self.step, inclusive=True)
        self.slices = [(zl, self._slice(zl)) for zl in r]

    def _slice(self, delta):
        normal = self.basis.normal().normalized()
        stepped = self.basis + (normal * delta)
        base = PlanarPolygon(stepped, self.slice)
        slicer = PolygonExtrusion(base, normal * self.step)
        plane = Plane(stepped.origin, stepped.origin + stepped.bx, stepped.origin + stepped.by)
        qs = geometry.quantum ** 2
        planar = [p for p in (slicer * self.solid).polygons
                  if all(plane.connect(pt).magnitude_squared() < qs for pt in p.points)]
        planar = [p.simplify() for p in planar]
        planar = [p for p in planar if p is not None and len(p.points) > 2]
        return decompose.rebuild(planar)
