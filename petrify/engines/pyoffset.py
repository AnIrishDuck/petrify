from ..plane import ComplexPolygon, Line, LineSegment, Polygon, Point, Ray
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
    return Ray(shifted.points[1], magnitude(a.v, ai, ai + bi))

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
    if solution[0] < 0 or solution[0] > 1:
        return None
    else:
        return (line.p + line.v * solution[0] + normal * solution[1], solution[1])

def safe_find_collision(line, normal, vertex, inwards):
    try:
        return find_collision(line, normal, vertex, inwards)
    except ZeroDivisionError:
        return None

def find_collisions(ray, segments, inwards):
    initial = (
        ((other, ray.p), safe_find_collision(other, inwards[other], ray.p, ray.v))
        for other in segments if other.p1 != ray.p and other.p2 != ray.p
    )
    initial = ((a, b) for a, b in initial if b)
    return [(pair, p, o) for pair, (p, o) in initial if o > 0]

def inner_properties(polygon):
    segments = polygon.segments()

    inwards = {s: find_inward_ray(polygon, s) for s in segments}

    return (segments, inwards)

def to_rays(polygon):
    return [offset_inward_ray(polygon, ix) for ix in range(len(polygon))]

def shift(l, n):
    return [*l[n:], *l[:n]]

def partition(rays, cut_i, line_i):
    shifted = shift(rays, line_i + 1)
    a, b = [], []
    splitter = rays[cut_i]
    split = False
    for ray in shifted:
        if ray == splitter:
            split = True
        elif not split:
            a.append(ray)
        else:
            b.append(ray)
    return a, b

def find_merge_ray(a, b, line, inwards):
    segment = LineSegment(a, b)
    new_vertex = Line(segment.p1, segment.p2).intersect(Line(line.p1, line.p2))
    ai = inwards[segment]
    bi = inwards[line]
    return Ray(new_vertex, magnitude(segment.v, ai, ai + bi))

def find_first_split_event(rays):
    polygon = Polygon([ray.p for ray in rays])
    segments, inwards = inner_properties(polygon)

    all_collisions = [find_collisions(ray, segments, inwards) for ray in rays]
    solutions = [
        min(collisions, key=lambda t: t[2])
        for collisions in all_collisions if collisions
    ]

    (segment, cut), point, offset = min(solutions, key=lambda t: t[2])

    cut_i = polygon.index_of(cut)
    line_i = polygon.index_of(segment.p1)

    cut = polygon.points[cut_i]
    line = LineSegment(polygon.points[line_i], polygon.points[(line_i + 1) % len(polygon.points)])
    a, b = partition(rays, cut_i, line_i)
    a = [*a, find_merge_ray(a[-1].p, cut, line, inwards)] if len(a) > 1 else []
    b = [find_merge_ray(cut, b[0].p, line, inwards), *b] if len(b) > 1 else []

    return (offset, [_rays for _rays in (a, b) if _rays])

def safe_find_first_split_event(rays):
    try:
        return find_first_split_event(rays)
    except ZeroDivisionError:
        return None

def nonlocal_offset(complex, amount):
    all_rays = [to_rays(polygon) for polygon in complex.exterior]

    offsets = [(rays, safe_find_first_split_event(rays)) for rays in all_rays]
    amounts = [o[1][0] for o in offsets if o[1]]
    while amounts and amount >= min(amounts):
        all_rays = [
            rays
            for original, pair in offsets
            for rays in ([original] if not pair or pair[0] > amount else pair[1])
        ]
        offsets = [(rays, safe_find_first_split_event(rays)) for rays in all_rays]
        amounts = [o[1][0] for o in offsets if o[1]]

    return ComplexPolygon([
        Polygon([ray.p + ray.v * amount for ray in polygon])
        for polygon in all_rays
    ])
