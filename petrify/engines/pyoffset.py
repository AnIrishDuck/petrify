from ..plane import ComplexPolygon, Polygon, Point, Ray
from ..solver import solve_matrix

def offset(polygon, amount):
    def off(ps, v):
        polygons = [p.offset(v) for p in ps]
        return [p for p in polygons if p is not None]

    return ComplexPolygon(
        interior=off(polygon.interior, -amount),
        exterior=off(polygon.exterior, amount)
    )

def magnitude(line, normal, inwards):
    # w * inwards = u * line.vector + normal
    # w * inwards - u * line.vector = normal
    rows = list(zip(inwards.xy, (-line).xy, normal))
    matrix = list(list(row) for row in rows)
    solution = solve_matrix(matrix)
    return inwards * solution[0]

def offset_inward_ray(polygon, ix):
    shifted = polygon.shift(ix - 1)
    segments = shifted.segments()

    a, b = segments[0], segments[1]
    ai, bi = polygon.inwards(a), polygon.inwards(b)
    return (shifted.points[1], magnitude(a.v, ai, ai + bi))

def find_inward_ray(polygon, edge):
    mid = (edge.p1 + edge.p2) / 2
    ray = Ray(Point(*mid), edge.v.cross())

    # NOTE: this still might have issues with parallel lines that intersect
    # the ray drawn from the midpoint along their entire span.
    intersections = (
        (other, ray.intersect(other)) for other in polygon.segments() if other != edge
    )

    # The intersection can be a point on the outside of the polygon. In this
    # case, it will intersect two segments, even though it has only crossed
    # the boundary of the polygon once. We arbitrarily ignore one of these
    # segments (via the != l.p2 check) to resolve this corner case.
    count = sum(
        1 for l, i in intersections
        if i is not None and i != l.p2
    )
    return (ray if count % 2 == 1 else -ray).v.normalized()

def find_collision(line, normal, vertex, inwards):
    # line.p + x * line.v + normal * y = vertex + y * inwards
    # x * line.v + (normal - inwards) * y = vertex - line.p
    rows = list(zip(line.v, (normal-inwards).xy, (vertex - line.p).xy))
    matrix = list(list(row) for row in rows)
    solution = solve_matrix(matrix)
    return (line.p + line.v * solution[0] + normal * solution[1], solution[1])

def find_collisions(v, segments, inwards, in_rays):
    initial = (
        ((other, v), find_collision(other, inwards[other], v, in_rays[v]))
        for other in segments if other.p1 != v and other.p2 != v
    )
    return ((pair, p, o) for pair, (p, o) in initial if o > 0)

def inner_properties(polygon):
    segments = polygon.segments()

    in_rays = dict(offset_inward_ray(polygon, ix) for ix in range(len(polygon)))
    inwards = {s: find_inward_ray(polygon, s) for s in segments}

    return (segments, in_rays, inwards)

def find_first_split_event(polygon):
    segments, in_rays, inwards = inner_properties(polygon)

    solutions = [
        min(find_collisions(v, segments, inwards, in_rays), key=lambda t: t[2])
        for v in polygon.points
    ]

    (segment, cut), point, offset = min(solutions, key=lambda t: t[2])

    cut_i = polygon.index_of(cut)
    line_i = polygon.index_of(segment.p1)

    a = [p + in_rays[p] * offset for p in (*polygon.points[0:line_i + 1], *polygon.points[cut_i:])]
    b = [p + in_rays[p] * offset for p in polygon.points[(line_i + 1):(cut_i + 1)]]
    return (offset, ComplexPolygon([Polygon(p) for p in (a, b) if p]))

def nonlocal_offset(complex, amount):
    offsets = [(polygon, find_first_split_event(polygon)) for polygon in complex.exterior]
    polygons = [
        p
        for original, (event_offset, split) in offsets
        for p in ([original] if event_offset > amount else split.polygons)
    ]
    return ComplexPolygon(polygons)
