import pint

u = pint.UnitRegistry()
u.define('file = [file]')

def parse_unit(v):
    return getattr(u, v) if isinstance(v, str) else v

def assert_lengthy(u):
    assert hasattr(u, 'magnitude'), "object does not have unit tag: {0!r}".format(u)
    assert u.check('[length]'), "does not have length units: {0!r}".format(u)
    return u

def conversion(scale):
    scale = parse_unit(scale)
    unit_or_quantity = isinstance(scale, u.Unit) or isinstance(scale, u.Quantity)
    assert unit_or_quantity, "object not unit or scale conversion: {0!r}".format(scale)
    if isinstance(scale, u.Unit):
        scale = (1 * scale) / u.file
    assert scale.check('[length] / [file]'), "does not have scaling units ([length] / [file]): {0!r}".format({scale.units})
    return scale
