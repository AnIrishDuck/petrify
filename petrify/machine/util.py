import math

def frange(a, b, step, inclusive=False):
    count = math.floor((b - a) / step) if a != b else 1
    for ix in range(0, count):
        v = a + (ix * step)
        if v != b: yield v

    if inclusive: yield b
