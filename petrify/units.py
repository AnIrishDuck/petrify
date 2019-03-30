import pint

u = pint.UnitRegistry()
u.define('file = [file]')

def parse_unit(v):
    return getattr(u, v) if isinstance(v, str) else v

def assert_lengthy(u):
    assert hasattr(u, 'magnitude'), f"object does not have unit tag: {u}"
    assert u.check('[length]'), f"does not have length units: {u}"
    return u

def conversion(scale):
    scale = parse_unit(scale)
    unit_or_quantity = isinstance(scale, u.Unit) or isinstance(scale, u.Quantity)
    assert unit_or_quantity, f"object not unit or scale conversion: {scale}"
    if isinstance(scale, u.Unit):
        scale = (1 * scale) / u.file
    assert scale.check('[length] / [file]'), f"does not have scaling units ([length] / [file]): {scale.units}"
    return scale
