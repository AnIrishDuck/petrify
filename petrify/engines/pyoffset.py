from ..plane import ComplexPolygon, Polygon
from ..solver import solve_matrix

def offset(polygon, amount):
    def off(ps, v):
        polygons = [p.offset(v) for p in ps]
        return [p for p in polygons if p is not None]

    return ComplexPolygon(
        interior=off(polygon.interior, -amount),
        exterior=off(polygon.exterior, amount)
    )

def offset_inward_ray(polygon, ix):
    def magnitude(line, normal, inwards):
        # w * inwards = u * line.vector + normal
        # w * inwards - u * line.vector = normal
        rows = list(zip(inwards.xy, (-line).xy, normal))
        matrix = list(list(row) for row in rows)
        solution = solve_matrix(matrix)
        return inwards * solution[0]

    shifted = polygon.shift(ix - 1)
    segments = shifted.segments()

    a, b = segments[0], segments[1]
    ai, bi = polygon.inwards(a), polygon.inwards(b)
    return (shifted.points[1], magnitude(a.v, ai, ai + bi))

def find_first_split_event(polygon):
    in_rays = dict(offset_inward_ray(polygon, ix) for ix in range(len(polygon)))
    def solve(line, normal, vertex, inwards):
        # line.p + x * line.v + normal * y = vertex + y * inwards
        # x * line.v + (normal - inwards) * y = vertex - line.p
        rows = list(zip(line.v, (normal-inwards).xy, (vertex - line.p).xy))
        matrix = list(list(row) for row in rows)
        solution = solve_matrix(matrix)
        return (line.p + line.v * solution[0] + normal * solution[1], solution[1])

    def find_solutions(v):
        initial = (
            ((other, v), solve(other, polygon.inwards(other), v, in_rays[v]))
            for other in segments if other.p1 != v and other.p2 != v
        )
        return ((pair, p, o) for pair, (p, o) in initial if o > 0)

    segments = polygon.segments()

    solutions = [
        min(find_solutions(v), key=lambda t: t[2])
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
