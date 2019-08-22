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
