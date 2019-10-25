from .solver import solve_matrix

def index_by(it, f):
    # why this isn't a stdlib function like in every other sane language escapes
    # me...
    d = {}
    for i in it:
        k = f(i)
        previous = d.get(k, [])
        previous.append(i)
        d[k] = previous
    return d

def locate_circle(p, np, l):
    try:
        # l.p + l.v * x + l.normal * r == p + np * r
        # l.v * x + (l.n - pn) * r == p - l.p
        npn = np.normalized()
        nl = l.v.cross().normalized()
        c = p - l.p
        b = (nl - npn)
        a = l.v.normalized()
        rows = zip(a.xy, b.xy, c.xy)
        x, r = solve_matrix(list(list(row) for row in rows))
        x = x / l.v.magnitude()
        if x < 0 or x > 1: return None
        return [p + npn * r, r, x]
    except ZeroDivisionError:
        return None
