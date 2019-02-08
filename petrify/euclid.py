#!/usr/bin/env python
#
# euclid graphics maths module
#
# Copyright (c) 2006 Alex Holkner <Alex.Holkner@mail.google.com>
# Copyright (c) 2011 Eugen Zagorodniy <https://github.com/ezag/>
# Copyright (c) 2011 Dov Grobgeld <https://github.com/dov>
# Copyright (c) 2012 Lorenzo Riano <https://github.com/lorenzoriano>
# Copyright (c) 2019 Frank Murphy <https://github.com/anirishduck>
#
# This library is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation; either version 2.1 of the License, or (at your
# option) any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

"""
Ported from pyeuclid.

Used to perform all basic 2d / 3d calculations, and for constructions of all
solid objects.

"""

import math
import operator
import types

# Some magic here.  If _use_slots is True, the classes will derive from
# object and will define a __slots__ class variable.  If _use_slots is
# False, classes will be old-style and will not define __slots__.
#
# _use_slots = True:   Memory efficient, probably faster in future versions
#                      of Python, "better".
# _use_slots = False:  Ordinary classes, much faster than slots in current
#                      versions of Python (2.4 and 2.5).
_use_slots = True

# If True, allows components of Vector2 and Vector3 to be set via swizzling;
# e.g.  v.xyz = (1, 2, 3).  This is much, much slower than the more verbose
# v.x = 1; v.y = 2; v.z = 3,  and slows down ordinary element setting as
# well.  Recommended setting is False.
_enable_swizzle_set = False

# Requires class to derive from object.
if _enable_swizzle_set:
    _use_slots = True

# Implement _use_slots magic.
class _EuclidMetaclass(type):
    def __new__(cls, name, bases, dct):
        if '__slots__' in dct:
            dct['__getstate__'] = cls._create_getstate(dct['__slots__'])
            dct['__setstate__'] = cls._create_setstate(dct['__slots__'])
        if _use_slots:
            return type.__new__(cls, name, bases + (object,), dct)
        else:
            if '__slots__' in dct:
                del dct['__slots__']
            return types.ClassType.__new__(types.ClassType, name, bases, dct)

    @classmethod
    def _create_getstate(cls, slots):
        def __getstate__(self):
            d = {}
            for slot in slots:
                d[slot] = getattr(self, slot)
            return d
        return __getstate__

    @classmethod
    def _create_setstate(cls, slots):
        def __setstate__(self, state):
            for name, value in state.items():
                setattr(self, name, value)
        return __setstate__

__metaclass__ = _EuclidMetaclass
