"""
Commonly used conversions between measurement systems:

>>> mm_to_in
Vector(25.4, 25.4, 25.4)
>>> in_to_mm.rounded(4)
Vector(0.0394, 0.0394, 0.0394)

"""
from .space import Vector

mm_p_in = 25.4
mm_to_in = Vector(mm_p_in, mm_p_in, mm_p_in)
in_to_mm = Vector(1 / mm_p_in, 1 / mm_p_in, 1 / mm_p_in)
