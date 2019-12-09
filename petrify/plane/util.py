import math
from .point import Point2, Vector2

def _intersect_point2_circle(P, C):
    return abs(P - C.c) <= C.r

def _intersect_line2_line2(A, B):
    d = B.v.y * A.v.x - B.v.x * A.v.y
    if d == 0:
        return None

    dy = A.p.y - B.p.y
    dx = A.p.x - B.p.x
    ua = (B.v.x * dy - B.v.y * dx) / d
    if not A._u_in(ua):
        return None
    ub = (A.v.x * dy - A.v.y * dx) / d
    if not B._u_in(ub):
        return None

    return Point2(A.p.x + ua * A.v.x,
                  A.p.y + ua * A.v.y)

def _intersect_line2_circle(L, C):
    from . import LineSegment2
    a = L.v.magnitude_squared()
    b = 2 * (L.v.x * (L.p.x - C.c.x) + \
             L.v.y * (L.p.y - C.c.y))
    c = C.c.magnitude_squared() + \
        L.p.magnitude_squared() - \
        2 * C.c.dot(L.p) - \
        C.r ** 2
    det = b ** 2 - 4 * a * c
    if det < 0:
        return None
    sq = math.sqrt(det)
    u1 = (-b + sq) / (2 * a)
    u2 = (-b - sq) / (2 * a)

    if u1 * u2 > 0 and not L._u_in(u1) and not L._u_in(u2):
        return None

    if not L._u_in(u1):
        u1 = max(min(u1, 1.0), 0.0)
    if not L._u_in(u2):
        u2 = max(min(u2, 1.0), 0.0)

    # Tangent
    if u1 == u2:
        return Point2(L.p.x + u1 * L.v.x,
                      L.p.y + u1 * L.v.y)

    return LineSegment2(Point2(L.p.x + u1 * L.v.x,
                               L.p.y + u1 * L.v.y),
                        Point2(L.p.x + u2 * L.v.x,
                               L.p.y + u2 * L.v.y))

def _intersect_circle_circle(A, B):
    d = abs(A.c - B.c)
    s = A.r + B.r
    m = abs(A.r - B.r)
    if d > s or d < m:
        return None
    d2 = d ** 2
    s2 = s ** 2
    m2 = m ** 2
    k = 0.25 * math.sqrt((s2 - d2) * (d2 - m2))
    dr = (A.r ** 2 - B.r ** 2) / d2
    kd = 2 * k / d2
    return (
      Point2(
        0.5 * (A.c.x + B.c.x + (B.c.x - A.c.x) * dr) + (B.c.y - A.c.y) * kd,
        0.5 * (A.c.y + B.c.y + (B.c.y - A.c.y) * dr) - (B.c.x - A.c.x) * kd),
      Point2(
        0.5 * (A.c.x + B.c.x + (B.c.x - A.c.x) * dr) - (B.c.y - A.c.y) * kd,
        0.5 * (A.c.y + B.c.y + (B.c.y - A.c.y) * dr) + (B.c.x - A.c.x) * kd))

def _connect_point2_line2(P, L):
    from . import LineSegment2
    d = L.v.magnitude_squared()
    assert d != 0
    u = ((P.x - L.p.x) * L.v.x + \
         (P.y - L.p.y) * L.v.y) / d
    if not L._u_in(u):
        u = max(min(u, 1.0), 0.0)
    return LineSegment2(P,
                        Point2(L.p.x + u * L.v.x,
                               L.p.y + u * L.v.y))

def _connect_point2_circle(P, C):
    from . import LineSegment2
    v = P - C.c
    v = v.normalized()
    v *= C.r
    return LineSegment2(P, Point2(C.c.x + v.x, C.c.y + v.y))

def _connect_line2_line2(A, B):
    from . import LineSegment2
    d = B.v.y * A.v.x - B.v.x * A.v.y
    if d == 0:
        # Parallel, connect an endpoint with a line
        if isinstance(B, Ray2) or isinstance(B, LineSegment2):
            p1, p2 = _connect_point2_line2(B.p, A)
            return p2, p1
        # No endpoint (or endpoint is on A), possibly choose arbitrary point
        # on line.
        return _connect_point2_line2(A.p, B)

    dy = A.p.y - B.p.y
    dx = A.p.x - B.p.x
    ua = (B.v.x * dy - B.v.y * dx) / d
    if not A._u_in(ua):
        ua = max(min(ua, 1.0), 0.0)
    ub = (A.v.x * dy - A.v.y * dx) / d
    if not B._u_in(ub):
        ub = max(min(ub, 1.0), 0.0)

    return LineSegment2(Point2(A.p.x + ua * A.v.x, A.p.y + ua * A.v.y),
                        Point2(B.p.x + ub * B.v.x, B.p.y + ub * B.v.y))

def _connect_circle_line2(C, L):
    from . import LineSegment2
    d = L.v.magnitude_squared()
    assert d != 0
    u = ((C.c.x - L.p.x) * L.v.x + (C.c.y - L.p.y) * L.v.y) / d
    if not L._u_in(u):
        u = max(min(u, 1.0), 0.0)
    point = Point2(L.p.x + u * L.v.x, L.p.y + u * L.v.y)
    v = (point - C.c)
    v = v.normalized()
    v *= C.r
    return LineSegment2(Point2(C.c.x + v.x, C.c.y + v.y), point)

def _connect_circle_circle(A, B):
    from . import LineSegment2
    v = B.c - A.c
    d = v.magnitude()
    if A.r >= B.r and d < A.r:
        #centre B inside A
        s1,s2 = +1, +1
    elif B.r > A.r and d < B.r:
        #centre A inside B
        s1,s2 = -1, -1
    elif d >= A.r and d >= B.r:
        s1,s2 = +1, -1
    v = v.normalized()
    return LineSegment2(Point2(A.c.x + s1 * v.x * A.r, A.c.y + s1 * v.y * A.r),
                        Point2(B.c.x + s2 * v.x * B.r, B.c.y + s2 * v.y * B.r))
