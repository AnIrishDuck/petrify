import sys, random
from petrify.solid import tau, Union, Box, Vector, Point
from petrify import engines

if len(sys.argv) > 1:
    engines.csg = getattr(engines, sys.argv[1])

def spin(shape):
    return (
        shape
            .rotate_around(random.uniform(0, tau / 8), Vector.basis.x)
            .rotate_around(random.uniform(0, tau / 8), Vector.basis.y)
            .rotate_around(random.uniform(0, tau / 8), Vector.basis.z)
    )

def delta(): return random.uniform(0.75, 1.25)

cubes = [
    spin(Box(
        Point.origin,
        random.uniform(1, 2) * Vector(1, 1, 1)
    )) + Point(x * delta(), y * delta(), delta())
    for x in range(10)
    for y in range(10)
]

Union(cubes)
