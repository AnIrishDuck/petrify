"""
Math utility library for common three-dimensional constructs:

- :py:class:`Vector`
- :py:class:`Point`
- :py:class:`Polygon`
- :py:class:`Plane`
- :py:class:`Quaternion`
- :py:class:`Matrix`
- :py:class:`Line`
- :py:class:`Ray`
- :py:class:`LineSegment`

The `pint`_ library can be used to specify dimensions:

>>> from petrify import u
>>> p = Point(50, 25, 50) * u.mm
>>> p.to('m')
<Quantity(Point(0.05, 0.025, 0.05), 'meter')>

Many methods are nominally supported when wrapped with `pint`. We recommend
you only use units when exporting and importing data, and pick a canonical unit
for all petrify operations.

Big thanks to pyeuclid, the source of most of the code here.

.. note::
    These examples and this library make heavy use of the `tau` constant for
    rotational math *instead* of Pi. Read why at the `Tau Manifesto`_.

.. _`pint`: https://pint.readthedocs.io/en/0.9/
.. _`Tau Manifesto`: https://tauday.com/tau-manifesto

"""
import math
import operator
import types

from pint.unit import _Unit

from .geometry import Geometry, tau, valid_scalar

class Vector:
    """
    A three-dimensional vector supporting all corresponding built-in math
    operators:

    >>> Vector(1, 2, 3) + Vector(2, 2, 2)
    Vector(3, 4, 5)
    >>> Vector(1, 2, 3) - Vector(2, 2, 2)
    Vector(-1, 0, 1)
    >>> Vector(1, 0, 1) * 5
    Vector(5, 0, 5)
    >>> Vector(1, 0, 1) / 5
    Vector(0.2, 0.0, 0.2)
    >>> Vector(1, 1, 1) == Vector(1, 1, 1)
    True

    In addition to many other specialized vector operations.

    Defines convenience `.basis` members for commonly used basis vectors:

    >>> Vector.basis.x; Vector.bx
    Vector(1, 0, 0)
    Vector(1, 0, 0)
    >>> Vector.basis.y; Vector.by
    Vector(0, 1, 0)
    Vector(0, 1, 0)
    >>> Vector.basis.z; Vector.bz
    Vector(0, 0, 1)
    Vector(0, 0, 1)

    """

    __slots__ = ['x', 'y', 'z']
    __hash__ = None

    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __copy__(self):
        return self.__class__(self.x, self.y, self.z)

    copy = __copy__

    def __repr__(self):
        return 'Vector({0!r}, {1!r}, {2!r})'.format(*self.xyz)

    def __eq__(self, other):
        if isinstance(other, Vector):
            return self.x == other.x and \
                   self.y == other.y and \
                   self.z == other.z
        else:
            assert hasattr(other, '__len__') and len(other) == 3
            return self.x == other[0] and \
                   self.y == other[1] and \
                   self.z == other[2]

    def __ne__(self, other):
        return not self.__eq__(other)

    def __nonzero__(self):
        return bool(self.x != 0 or self.y != 0 or self.z != 0)

    def __len__(self):
        return 3

    def __getitem__(self, key):
        return (self.x, self.y, self.z)[key]

    def __setitem__(self, key, value):
        l = [self.x, self.y, self.z]
        l[key] = value
        self.x, self.y, self.z = l

    def __iter__(self):
        return iter((self.x, self.y, self.z))

    def __getattr__(self, name):
        try:
            return tuple([(self.x, self.y, self.z)['xyz'.index(c)] \
                          for c in name])
        except ValueError:
            raise AttributeError(name)

    def __add__(self, other):
        if isinstance(other, Vector):
            # Vector + Vector -> Vector
            # Vector + Point -> Point
            # Point + Point -> Vector
            if self.__class__ is other.__class__:
                _class = Vector
            else:
                _class = Point
            return _class(self.x + other.x,
                          self.y + other.y,
                          self.z + other.z)
        else:
            assert hasattr(other, '__len__') and len(other) == 3
            return Vector(self.x + other[0],
                           self.y + other[1],
                           self.z + other[2])
    __radd__ = __add__

    def __iadd__(self, other):
        if isinstance(other, Vector):
            self.x += other.x
            self.y += other.y
            self.z += other.z
        else:
            self.x += other[0]
            self.y += other[1]
            self.z += other[2]
        return self

    def __sub__(self, other):
        if isinstance(other, Vector):
            # Vector - Vector -> Vector
            # Vector - Point -> Point
            # Point - Point -> Vector
            if self.__class__ is other.__class__:
                _class = Vector
            else:
                _class = Point
            return Vector(self.x - other.x,
                           self.y - other.y,
                           self.z - other.z)
        else:
            assert hasattr(other, '__len__') and len(other) == 3
            return Vector(self.x - other[0],
                           self.y - other[1],
                           self.z - other[2])


    def __rsub__(self, other):
        if isinstance(other, Vector):
            return Vector(other.x - self.x,
                           other.y - self.y,
                           other.z - self.z)
        else:
            assert hasattr(other, '__len__') and len(other) == 3
            return Vector(other.x - self[0],
                           other.y - self[1],
                           other.z - self[2])

    def __mul__(self, other):
        if isinstance(other, _Unit):
            assert (1 * other).check('[length]'), 'only compatible with length units'
            return NotImplemented
        elif valid_scalar(other):
            return self.__class__(self.x * other,
                                  self.y * other,
                                  self.z * other)
        else:
            return NotImplemented

    __rmul__ = __mul__

    def __div__(self, other):
        assert type(other) in (int, float)
        return Vector(operator.div(self.x, other),
                       operator.div(self.y, other),
                       operator.div(self.z, other))


    def __rdiv__(self, other):
        assert type(other) in (int, float)
        return Vector(operator.div(other, self.x),
                       operator.div(other, self.y),
                       operator.div(other, self.z))

    def __floordiv__(self, other):
        assert type(other) in (int, float)
        return Vector(operator.floordiv(self.x, other),
                       operator.floordiv(self.y, other),
                       operator.floordiv(self.z, other))


    def __rfloordiv__(self, other):
        assert type(other) in (int, float)
        return Vector(operator.floordiv(other, self.x),
                       operator.floordiv(other, self.y),
                       operator.floordiv(other, self.z))

    def __truediv__(self, other):
        assert type(other) in (int, float)
        return Vector(operator.truediv(self.x, other),
                       operator.truediv(self.y, other),
                       operator.truediv(self.z, other))


    def __rtruediv__(self, other):
        assert type(other) in (int, float)
        return Vector(operator.truediv(other, self.x),
                       operator.truediv(other, self.y),
                       operator.truediv(other, self.z))

    def __neg__(self):
        return Vector(-self.x,
                        -self.y,
                        -self.z)

    __pos__ = __copy__

    def __abs__(self):
        return math.sqrt(self.x ** 2 + \
                         self.y ** 2 + \
                         self.z ** 2)

    magnitude = __abs__

    def magnitude_squared(self):
        return self.x ** 2 + \
               self.y ** 2 + \
               self.z ** 2

    def normalize(self):
        d = self.magnitude()
        if d:
            self.x /= d
            self.y /= d
            self.z /= d
        return self

    def normalized(self):
        """ Returns a vector with the same direction but unit (1) length. """
        d = self.magnitude()
        if d:
            return Vector(self.x / d,
                           self.y / d,
                           self.z / d)
        return self.copy()

    def rounded(self, place=None):
        """
        Rounds all elements to `place` decimals.

        """
        return self.__class__(*(round(v, place) for v in self.xyz))

    def dot(self, other):
        """ The dot product of this vector and the `other`. """
        assert isinstance(other, Vector)
        return self.x * other.x + \
               self.y * other.y + \
               self.z * other.z

    def cross(self, other):
        """ The cross product of this vector and the `other`. """
        assert isinstance(other, Vector)
        return Vector(self.y * other.z - self.z * other.y,
                       -self.x * other.z + self.z * other.x,
                       self.x * other.y - self.y * other.x)

    def reflect(self, normal):
        """
        Reflect this vector across a plane with the given `normal`

        .. note::
            Assumes the given `normal` has unit (1) length.
        """
        # assume normal is normalized
        assert isinstance(normal, Vector)
        d = 2 * (self.x * normal.x + self.y * normal.y + self.z * normal.z)
        return Vector(self.x - d * normal.x,
                       self.y - d * normal.y,
                       self.z - d * normal.z)

    def rotate_around(self, axis, theta):
        """
        Return a new vector rotated around `axis` by angle `theta`. Right hand
        rule applies.

        """

        # Adapted from equations published by Glenn Murray.
        # http://inside.mines.edu/~gmurray/ArbitraryAxisRotation/ArbitraryAxisRotation.html
        x, y, z = self.x, self.y,self.z
        u, v, w = axis.x, axis.y, axis.z

        # Extracted common factors for simplicity and efficiency
        r2 = u**2 + v**2 + w**2
        r = math.sqrt(r2)
        ct = math.cos(theta)
        st = math.sin(theta) / r
        dt = (u*x + v*y + w*z) * (1 - ct) / r2
        return Vector((u * dt + x * ct + (-w * y + v * z) * st),
                       (v * dt + y * ct + ( w * x - u * z) * st),
                       (w * dt + z * ct + (-v * x + u * y) * st))

    def angle(self, other):
        """ Return the angle to the vector other. """
        return math.acos(self.dot(other) / (self.magnitude()*other.magnitude()))

    def project(self, other):
        """ Return one vector projected on the vector other. """
        n = other.normalized()
        return self.dot(n)*n

    def snap(self, grid):
        """
        Snaps this vector to a `grid`:

        >>> Vector(1.15, 1.15, 0.9).snap(0.25)
        Vector(1.25, 1.25, 1.0)

        """
        def snap(v):
            return round(v / grid) * grid
        return self.__class__(snap(self.x), snap(self.y), snap(self.z))

    class Basis:
        @property
        def x(self): return Vector(1, 0, 0)

        @property
        def y(self): return Vector(0, 1, 0)

        @property
        def z(self): return Vector(0, 0, 1)
    basis = Basis()

Vector.bx = Vector.basis.x
Vector.by = Vector.basis.y
Vector.bz = Vector.basis.z

class Polygon:
    """
    A linear cycle of coplanar convex points:

    >>> triangle = Polygon([Point(0, 0, 0), Point(0, 2, 0), Point(1, 1, 0)])

    """

    def __init__(self, points):
        self.points = points
        self.plane = Plane(*points[0:3])

    def segments(self):
        """ Returns all line segments composing this polygon's edges. """
        paired = zip(self.points, self.points[1:] + [self.points[0]])
        return [LineSegment(a, b) for a, b in paired]

    def has_edge(self, edge):
        """ Returns true if this polygon contains the given `edge`. """
        return any(l == edge for l in self.segments())

    def __repr__(self):
        return "Polygon({0!r})".format(self.points)

# a b c d
# e f g h
# i j k l
# m n o p
class Matrix:
    """
    A matrix that can be used to perform common transformations on
    three-dimensional points and vectors:

    >>> Matrix.scale(*Vector(1, 2, 1).xyz) * Point(1, 1, 1)
    Point(1, 2, 1)

    """
    __slots__ = list('abcdefghijklmnop')

    def __init__(self):
        self.a = self.f = self.k = self.p = 1.
        self.b = self.c = self.d = self.e = self.g = self.h = \
        self.i = self.j = self.l = self.m = self.n = self.o = 0

    def __copy__(self):
        M = Matrix()
        M.a = self.a
        M.b = self.b
        M.c = self.c
        M.d = self.d
        M.e = self.e
        M.f = self.f
        M.g = self.g
        M.h = self.h
        M.i = self.i
        M.j = self.j
        M.k = self.k
        M.l = self.l
        M.m = self.m
        M.n = self.n
        M.o = self.o
        M.p = self.p
        return M

    copy = __copy__

    def __repr__(self):
        return ('Matrix([% 8.2f % 8.2f % 8.2f % 8.2f\n'  \
                '         % 8.2f % 8.2f % 8.2f % 8.2f\n'  \
                '         % 8.2f % 8.2f % 8.2f % 8.2f\n'  \
                '         % 8.2f % 8.2f % 8.2f % 8.2f])') \
                % (self.a, self.b, self.c, self.d,
                   self.e, self.f, self.g, self.h,
                   self.i, self.j, self.k, self.l,
                   self.m, self.n, self.o, self.p)

    def __getitem__(self, key):
        return [self.a, self.e, self.i, self.m,
                self.b, self.f, self.j, self.n,
                self.c, self.g, self.k, self.o,
                self.d, self.h, self.l, self.p][key]

    def __setitem__(self, key, value):
        L = self[:]
        L[key] = value
        (self.a, self.e, self.i, self.m,
         self.b, self.f, self.j, self.n,
         self.c, self.g, self.k, self.o,
         self.d, self.h, self.l, self.p) = L

    def __mul__(self, other):
        if isinstance(other, Matrix):
            # Caching repeatedly accessed attributes in local variables
            # apparently increases performance by 20%.  Attrib: Will McGugan.
            Aa = self.a
            Ab = self.b
            Ac = self.c
            Ad = self.d
            Ae = self.e
            Af = self.f
            Ag = self.g
            Ah = self.h
            Ai = self.i
            Aj = self.j
            Ak = self.k
            Al = self.l
            Am = self.m
            An = self.n
            Ao = self.o
            Ap = self.p
            Ba = other.a
            Bb = other.b
            Bc = other.c
            Bd = other.d
            Be = other.e
            Bf = other.f
            Bg = other.g
            Bh = other.h
            Bi = other.i
            Bj = other.j
            Bk = other.k
            Bl = other.l
            Bm = other.m
            Bn = other.n
            Bo = other.o
            Bp = other.p
            C = Matrix()
            C.a = Aa * Ba + Ab * Be + Ac * Bi + Ad * Bm
            C.b = Aa * Bb + Ab * Bf + Ac * Bj + Ad * Bn
            C.c = Aa * Bc + Ab * Bg + Ac * Bk + Ad * Bo
            C.d = Aa * Bd + Ab * Bh + Ac * Bl + Ad * Bp
            C.e = Ae * Ba + Af * Be + Ag * Bi + Ah * Bm
            C.f = Ae * Bb + Af * Bf + Ag * Bj + Ah * Bn
            C.g = Ae * Bc + Af * Bg + Ag * Bk + Ah * Bo
            C.h = Ae * Bd + Af * Bh + Ag * Bl + Ah * Bp
            C.i = Ai * Ba + Aj * Be + Ak * Bi + Al * Bm
            C.j = Ai * Bb + Aj * Bf + Ak * Bj + Al * Bn
            C.k = Ai * Bc + Aj * Bg + Ak * Bk + Al * Bo
            C.l = Ai * Bd + Aj * Bh + Ak * Bl + Al * Bp
            C.m = Am * Ba + An * Be + Ao * Bi + Ap * Bm
            C.n = Am * Bb + An * Bf + Ao * Bj + Ap * Bn
            C.o = Am * Bc + An * Bg + Ao * Bk + Ap * Bo
            C.p = Am * Bd + An * Bh + Ao * Bl + Ap * Bp
            return C
        elif isinstance(other, Point):
            A = self
            B = other
            P = Point(0, 0, 0)
            P.x = A.a * B.x + A.b * B.y + A.c * B.z + A.d
            P.y = A.e * B.x + A.f * B.y + A.g * B.z + A.h
            P.z = A.i * B.x + A.j * B.y + A.k * B.z + A.l
            return P
        elif isinstance(other, Vector):
            A = self
            B = other
            V = Vector(0, 0, 0)
            V.x = A.a * B.x + A.b * B.y + A.c * B.z
            V.y = A.e * B.x + A.f * B.y + A.g * B.z
            V.z = A.i * B.x + A.j * B.y + A.k * B.z
            return V
        else:
            other = other.copy()
            other._apply_transform(self)
            return other

    def __imul__(self, other):
        assert isinstance(other, Matrix)
        # Caching repeatedly accessed attributes in local variables
        # apparently increases performance by 20%.  Attrib: Will McGugan.
        Aa = self.a
        Ab = self.b
        Ac = self.c
        Ad = self.d
        Ae = self.e
        Af = self.f
        Ag = self.g
        Ah = self.h
        Ai = self.i
        Aj = self.j
        Ak = self.k
        Al = self.l
        Am = self.m
        An = self.n
        Ao = self.o
        Ap = self.p
        Ba = other.a
        Bb = other.b
        Bc = other.c
        Bd = other.d
        Be = other.e
        Bf = other.f
        Bg = other.g
        Bh = other.h
        Bi = other.i
        Bj = other.j
        Bk = other.k
        Bl = other.l
        Bm = other.m
        Bn = other.n
        Bo = other.o
        Bp = other.p
        self.a = Aa * Ba + Ab * Be + Ac * Bi + Ad * Bm
        self.b = Aa * Bb + Ab * Bf + Ac * Bj + Ad * Bn
        self.c = Aa * Bc + Ab * Bg + Ac * Bk + Ad * Bo
        self.d = Aa * Bd + Ab * Bh + Ac * Bl + Ad * Bp
        self.e = Ae * Ba + Af * Be + Ag * Bi + Ah * Bm
        self.f = Ae * Bb + Af * Bf + Ag * Bj + Ah * Bn
        self.g = Ae * Bc + Af * Bg + Ag * Bk + Ah * Bo
        self.h = Ae * Bd + Af * Bh + Ag * Bl + Ah * Bp
        self.i = Ai * Ba + Aj * Be + Ak * Bi + Al * Bm
        self.j = Ai * Bb + Aj * Bf + Ak * Bj + Al * Bn
        self.k = Ai * Bc + Aj * Bg + Ak * Bk + Al * Bo
        self.l = Ai * Bd + Aj * Bh + Ak * Bl + Al * Bp
        self.m = Am * Ba + An * Be + Ao * Bi + Ap * Bm
        self.n = Am * Bb + An * Bf + Ao * Bj + Ap * Bn
        self.o = Am * Bc + An * Bg + Ao * Bk + Ap * Bo
        self.p = Am * Bd + An * Bh + Ao * Bl + Ap * Bp
        return self

    def transform(self, other):
        A = self
        B = other
        P = Point(0, 0, 0)
        P.x = A.a * B.x + A.b * B.y + A.c * B.z + A.d
        P.y = A.e * B.x + A.f * B.y + A.g * B.z + A.h
        P.z = A.i * B.x + A.j * B.y + A.k * B.z + A.l
        w =   A.m * B.x + A.n * B.y + A.o * B.z + A.p
        if w != 0:
            P.x /= w
            P.y /= w
            P.z /= w
        return P

    def transpose(self):
        (self.a, self.e, self.i, self.m,
         self.b, self.f, self.j, self.n,
         self.c, self.g, self.k, self.o,
         self.d, self.h, self.l, self.p) = \
        (self.a, self.b, self.c, self.d,
         self.e, self.f, self.g, self.h,
         self.i, self.j, self.k, self.l,
         self.m, self.n, self.o, self.p)

    def transposed(self):
        M = self.copy()
        M.transpose()
        return M

    # Static constructors
    @classmethod
    def new(cls, *values):
        """ Create a new matrix from the provided `values` array. """
        M = cls()
        M[:] = values
        return M

    @classmethod
    def identity(cls):
        """
        The identity transform:

        >>> Matrix.identity() * Point(1, 1, 1)
        Point(1.0, 1.0, 1.0)

        """
        self = cls()
        return self

    @classmethod
    def scale(cls, x, y, z):
        """
        A scale transform:

        >>> Matrix.scale(*Vector(1, 2, 1).xyz) * Point(1, 1, 1)
        Point(1, 2, 1)

        """
        self = cls()
        self.a = x
        self.f = y
        self.k = z
        return self

    @classmethod
    def translate(cls, x, y, z):
        """
        A translation transform:

        >>> Matrix.translate(*Vector(1, 2, 1).xyz) * Point(1, 1, 1)
        Point(2.0, 3.0, 2.0)

        """
        self = cls()
        self.d = x
        self.h = y
        self.l = z
        return self

    @classmethod
    def rotate_axis(cls, angle, axis):
        """
        A rotational transform:

        >>> (Matrix.rotate_axis(tau / 4, Vector.basis.z) * Point(1, 0, 0)).rounded()
        Point(0, 1, 0)

        """
        assert(isinstance(axis, Vector))
        vector = axis.normalized()
        x = vector.x
        y = vector.y
        z = vector.z

        self = cls()
        s = math.sin(angle)
        c = math.cos(angle)
        c1 = 1. - c

        # from the glRotate man page
        self.a = x * x * c1 + c
        self.b = x * y * c1 - z * s
        self.c = x * z * c1 + y * s
        self.e = y * x * c1 + z * s
        self.f = y * y * c1 + c
        self.g = y * z * c1 - x * s
        self.i = x * z * c1 - y * s
        self.j = y * z * c1 + x * s
        self.k = z * z * c1 + c
        return self

    @classmethod
    def rotate_euler(cls, heading, attitude, bank):
        # from http://www.euclideanspace.com/
        ch = math.cos(heading)
        sh = math.sin(heading)
        ca = math.cos(attitude)
        sa = math.sin(attitude)
        cb = math.cos(bank)
        sb = math.sin(bank)

        self = cls()
        self.a = ch * ca
        self.b = sh * sb - ch * sa * cb
        self.c = ch * sa * sb + sh * cb
        self.e = sa
        self.f = ca * cb
        self.g = -ca * sb
        self.i = -sh * ca
        self.j = sh * sa * cb + ch * sb
        self.k = -sh * sa * sb + ch * cb
        return self

    @classmethod
    def rotate_triple_axis(cls, x, y, z):
      m = cls()

      m.a, m.b, m.c = x.x, y.x, z.x
      m.e, m.f, m.g = x.y, y.y, z.y
      m.i, m.j, m.k = x.z, y.z, z.z

      return m

    @classmethod
    def look_at(cls, eye, at, up):
      z = (eye - at).normalized()
      x = up.cross(z).normalized()
      y = z.cross(x)

      m = cls.rotate_triple_axis(x, y, z)
      m.transpose()
      m.d, m.h, m.l = -x.dot(eye), -y.dot(eye), -z.dot(eye)
      return m

    @classmethod
    def perspective(cls, fov_y, aspect, near, far):
        # from the gluPerspective man page
        f = 1 / math.tan(fov_y / 2)
        self = cls()
        assert near != 0.0 and near != far
        self.a = f / aspect
        self.f = f
        self.k = (far + near) / (near - far)
        self.l = 2 * far * near / (near - far)
        self.o = -1
        self.p = 0
        return self

    def determinant(self):
        return ((self.a * self.f - self.e * self.b)
              * (self.k * self.p - self.o * self.l)
              - (self.a * self.j - self.i * self.b)
              * (self.g * self.p - self.o * self.h)
              + (self.a * self.n - self.m * self.b)
              * (self.g * self.l - self.k * self.h)
              + (self.e * self.j - self.i * self.f)
              * (self.c * self.p - self.o * self.d)
              - (self.e * self.n - self.m * self.f)
              * (self.c * self.l - self.k * self.d)
              + (self.i * self.n - self.m * self.j)
              * (self.c * self.h - self.g * self.d))

    def inverse(self):
        tmp = Matrix()
        d = self.determinant();

        if abs(d) < 0.001:
            # No inverse, return identity
            return tmp
        else:
            d = 1.0 / d;

            tmp.a = d * (self.f * (self.k * self.p - self.o * self.l) + self.j * (self.o * self.h - self.g * self.p) + self.n * (self.g * self.l - self.k * self.h));
            tmp.e = d * (self.g * (self.i * self.p - self.m * self.l) + self.k * (self.m * self.h - self.e * self.p) + self.o * (self.e * self.l - self.i * self.h));
            tmp.i = d * (self.h * (self.i * self.n - self.m * self.j) + self.l * (self.m * self.f - self.e * self.n) + self.p * (self.e * self.j - self.i * self.f));
            tmp.m = d * (self.e * (self.n * self.k - self.j * self.o) + self.i * (self.f * self.o - self.n * self.g) + self.m * (self.j * self.g - self.f * self.k));

            tmp.b = d * (self.j * (self.c * self.p - self.o * self.d) + self.n * (self.k * self.d - self.c * self.l) + self.b * (self.o * self.l - self.k * self.p));
            tmp.f = d * (self.k * (self.a * self.p - self.m * self.d) + self.o * (self.i * self.d - self.a * self.l) + self.c * (self.m * self.l - self.i * self.p));
            tmp.j = d * (self.l * (self.a * self.n - self.m * self.b) + self.p * (self.i * self.b - self.a * self.j) + self.d * (self.m * self.j - self.i * self.n));
            tmp.n = d * (self.i * (self.n * self.c - self.b * self.o) + self.m * (self.b * self.k - self.j * self.c) + self.a * (self.j * self.o - self.n * self.k));

            tmp.c = d * (self.n * (self.c * self.h - self.g * self.d) + self.b * (self.g * self.p - self.o * self.h) + self.f * (self.o * self.d - self.c * self.p));
            tmp.g = d * (self.o * (self.a * self.h - self.e * self.d) + self.c * (self.e * self.p - self.m * self.h) + self.g * (self.m * self.d - self.a * self.p));
            tmp.k = d * (self.p * (self.a * self.f - self.e * self.b) + self.d * (self.e * self.n - self.m * self.f) + self.h * (self.m * self.b - self.a * self.n));
            tmp.o = d * (self.m * (self.f * self.c - self.b * self.g) + self.a * (self.n * self.g - self.f * self.o) + self.e * (self.b * self.o - self.n * self.c));

            tmp.d = d * (self.b * (self.k * self.h - self.g * self.l) + self.f * (self.c * self.l - self.k * self.d) + self.j * (self.g * self.d - self.c * self.h));
            tmp.h = d * (self.c * (self.i * self.h - self.e * self.l) + self.g * (self.a * self.l - self.i * self.d) + self.k * (self.e * self.d - self.a * self.h));
            tmp.l = d * (self.d * (self.i * self.f - self.e * self.j) + self.h * (self.a * self.j - self.i * self.b) + self.l * (self.e * self.b - self.a * self.f));
            tmp.p = d * (self.a * (self.f * self.k - self.j * self.g) + self.e * (self.j * self.c - self.b * self.k) + self.i * (self.b * self.g - self.f * self.c));

        return tmp;

    def get_quaternion(self):
        """
        Returns a quaternion representing the rotation part of the matrix.

        """
        # Taken from:
        # http://web.archive.org/web/20041029003853/http://www.j3d.org/matrix_faq/matrfaq_latest.html#Q55
        trace = self.a + self.f + self.k

        if trace > 0.00000001: #avoid dividing by zero
            s = math.sqrt(1. + trace) * 2
            x = (self.j - self.g) / s
            y = (self.c - self.i) / s
            z = (self.e - self.b) / s
            w = 0.25 * s
        else:
            #this is really convenient to have now
            mat = (self.a, self.b, self.c, self.d,
                   self.e, self.f, self.g, self.h,
                   self.i, self.j, self.k, self.l,
                   self.m, self.n, self.o, self.p
                  )
            if ( mat[0] > mat[5] and mat[0] > mat[10] ):    #Column 0
                s  = math.sqrt( 1.0 + mat[0] - mat[5] - mat[10] ) * 2
                x = 0.25 * s
                y = (mat[4] + mat[1] ) / s
                z = (mat[2] + mat[8] ) / s
                w = (mat[9] - mat[6] ) / s
            elif ( mat[5] > mat[10] ):                     # Column 1
                s  = math.sqrt( 1.0 + mat[5] - mat[0] - mat[10] ) * 2
                x = (mat[4] + mat[1] ) / s
                y = 0.25 * s
                z = (mat[9] + mat[6] ) / s
                w = (mat[2] - mat[8] ) / s
            else:                                          # Column 2
                s  = math.sqrt( 1.0 + mat[10] - mat[0] - mat[5] ) * 2
                x = (mat[2] + mat[8] ) / s
                y = (mat[9] + mat[6] ) / s
                z = 0.25 * s
                w = (mat[4] - mat[1] ) / s

        return Quaternion(w, x, y, z)

class Quaternion:
    """
    Quaternions are composable representations of three-dimensional rotation
    operations.

    Multiplication can be performed on `Vector` instances to get the transformed
    vector or point:

    >>> r = Quaternion.rotate_axis(tau / 4, Vector.basis.x);
    >>> (r * Vector(0, 1, 0)).rounded()
    Vector(0, 0, 1)

    """

    # All methods and naming conventions based off
    # http://www.euclideanspace.com/maths/algebra/realNormedAlgebra/quaternions

    # w is the real part, (x, y, z) are the imaginary parts
    __slots__ = ['w', 'x', 'y', 'z']

    def __init__(self, w=1, x=0, y=0, z=0):
        self.w = w
        self.x = x
        self.y = y
        self.z = z

    def __copy__(self):
        Q = Quaternion()
        Q.w = self.w
        Q.x = self.x
        Q.y = self.y
        Q.z = self.z
        return Q

    copy = __copy__

    def __repr__(self):
        return 'Quaternion({0!r}, {1!r}, {2!r}, {3!r})'.format(self.w, self.x, self.y, self.z)

    def __mul__(self, other):
        if isinstance(other, Quaternion):
            Ax = self.x
            Ay = self.y
            Az = self.z
            Aw = self.w
            Bx = other.x
            By = other.y
            Bz = other.z
            Bw = other.w
            Q = Quaternion()
            Q.x =  Ax * Bw + Ay * Bz - Az * By + Aw * Bx
            Q.y = -Ax * Bz + Ay * Bw + Az * Bx + Aw * By
            Q.z =  Ax * By - Ay * Bx + Az * Bw + Aw * Bz
            Q.w = -Ax * Bx - Ay * By - Az * Bz + Aw * Bw
            return Q
        elif isinstance(other, Vector):
            w = self.w
            x = self.x
            y = self.y
            z = self.z
            Vx = other.x
            Vy = other.y
            Vz = other.z
            ww = w * w
            w2 = w * 2
            wx2 = w2 * x
            wy2 = w2 * y
            wz2 = w2 * z
            xx = x * x
            x2 = x * 2
            xy2 = x2 * y
            xz2 = x2 * z
            yy = y * y
            yz2 = 2 * y * z
            zz = z * z
            return other.__class__(\
               ww * Vx + wy2 * Vz - wz2 * Vy + \
               xx * Vx + xy2 * Vy + xz2 * Vz - \
               zz * Vx - yy * Vx,
               xy2 * Vx + yy * Vy + yz2 * Vz + \
               wz2 * Vx - zz * Vy + ww * Vy - \
               wx2 * Vz - xx * Vy,
               xz2 * Vx + yz2 * Vy + \
               zz * Vz - wy2 * Vx - yy * Vz + \
               wx2 * Vy - xx * Vz + ww * Vz)
        else:
            other = other.copy()
            other._apply_transform(self)
            return other

    def __imul__(self, other):
        assert isinstance(other, Quaternion)
        Ax = self.x
        Ay = self.y
        Az = self.z
        Aw = self.w
        Bx = other.x
        By = other.y
        Bz = other.z
        Bw = other.w
        self.x =  Ax * Bw + Ay * Bz - Az * By + Aw * Bx
        self.y = -Ax * Bz + Ay * Bw + Az * Bx + Aw * By
        self.z =  Ax * By - Ay * Bx + Az * Bw + Aw * Bz
        self.w = -Ax * Bx - Ay * By - Az * Bz + Aw * Bw
        return self

    def __abs__(self):
        return math.sqrt(self.w ** 2 + \
                         self.x ** 2 + \
                         self.y ** 2 + \
                         self.z ** 2)

    magnitude = __abs__

    def magnitude_squared(self):
        return self.w ** 2 + \
               self.x ** 2 + \
               self.y ** 2 + \
               self.z ** 2

    def identity(self):
        self.w = 1
        self.x = 0
        self.y = 0
        self.z = 0
        return self

    def rotate_axis(self, angle, axis):
        self *= Quaternion.rotate_axis(angle, axis)
        return self

    def rotate_euler(self, heading, attitude, bank):
        self *= Quaternion.rotate_euler(heading, attitude, bank)
        return self

    def rotate_matrix(self, m):
        self *= Quaternion.rotate_matrix(m)
        return self

    def conjugated(self):
        Q = Quaternion()
        Q.w = self.w
        Q.x = -self.x
        Q.y = -self.y
        Q.z = -self.z
        return Q

    def normalize(self):
        d = self.magnitude()
        if d != 0:
            self.w /= d
            self.x /= d
            self.y /= d
            self.z /= d
        return self

    def normalized(self):
        d = self.magnitude()
        if d != 0:
            Q = Quaternion()
            Q.w = self.w / d
            Q.x = self.x / d
            Q.y = self.y / d
            Q.z = self.z / d
            return Q
        else:
            return self.copy()

    def get_angle_axis(self):
        if self.w > 1:
            self = self.normalized()
        angle = 2 * math.acos(self.w)
        s = math.sqrt(1 - self.w ** 2)
        if s < 0.001:
            return angle, Vector(1, 0, 0)
        else:
            return angle, Vector(self.x / s, self.y / s, self.z / s)

    def get_euler(self):
        t = self.x * self.y + self.z * self.w
        if t > 0.4999:
            heading = 2 * math.atan2(self.x, self.w)
            attitude = math.pi / 2
            bank = 0
        elif t < -0.4999:
            heading = -2 * math.atan2(self.x, self.w)
            attitude = -math.pi / 2
            bank = 0
        else:
            sqx = self.x ** 2
            sqy = self.y ** 2
            sqz = self.z ** 2
            heading = math.atan2(2 * self.y * self.w - 2 * self.x * self.z,
                                 1 - 2 * sqy - 2 * sqz)
            attitude = math.asin(2 * t)
            bank = math.atan2(2 * self.x * self.w - 2 * self.y * self.z,
                              1 - 2 * sqx - 2 * sqz)
        return heading, attitude, bank

    def get_matrix(self):
        xx = self.x ** 2
        xy = self.x * self.y
        xz = self.x * self.z
        xw = self.x * self.w
        yy = self.y ** 2
        yz = self.y * self.z
        yw = self.y * self.w
        zz = self.z ** 2
        zw = self.z * self.w
        M = Matrix()
        M.a = 1 - 2 * (yy + zz)
        M.b = 2 * (xy - zw)
        M.c = 2 * (xz + yw)
        M.e = 2 * (xy + zw)
        M.f = 1 - 2 * (xx + zz)
        M.g = 2 * (yz - xw)
        M.i = 2 * (xz - yw)
        M.j = 2 * (yz + xw)
        M.k = 1 - 2 * (xx + yy)
        return M

    # Static constructors
    @classmethod
    def identity(cls):
        return cls()

    @classmethod
    def rotate_axis(cls, angle, axis):
        assert(isinstance(axis, Vector))
        axis = axis.normalized()
        s = math.sin(angle / 2)
        Q = cls()
        Q.w = math.cos(angle / 2)
        Q.x = axis.x * s
        Q.y = axis.y * s
        Q.z = axis.z * s
        return Q

    @classmethod
    def rotate_euler(cls, heading, attitude, bank):
        Q = cls()
        c1 = math.cos(heading / 2)
        s1 = math.sin(heading / 2)
        c2 = math.cos(attitude / 2)
        s2 = math.sin(attitude / 2)
        c3 = math.cos(bank / 2)
        s3 = math.sin(bank / 2)

        Q.w = c1 * c2 * c3 - s1 * s2 * s3
        Q.x = s1 * s2 * c3 + c1 * c2 * s3
        Q.y = s1 * c2 * c3 + c1 * s2 * s3
        Q.z = c1 * s2 * c3 - s1 * c2 * s3
        return Q

    @classmethod
    def rotate_matrix(cls, m):
      if m[0*4 + 0] + m[1*4 + 1] + m[2*4 + 2] > 0.00000001:
        t = m[0*4 + 0] + m[1*4 + 1] + m[2*4 + 2] + 1.0
        s = 0.5/math.sqrt(t)

        return cls(
          s*t,
          (m[1*4 + 2] - m[2*4 + 1])*s,
          (m[2*4 + 0] - m[0*4 + 2])*s,
          (m[0*4 + 1] - m[1*4 + 0])*s
          )

      elif m[0*4 + 0] > m[1*4 + 1] and m[0*4 + 0] > m[2*4 + 2]:
        t = m[0*4 + 0] - m[1*4 + 1] - m[2*4 + 2] + 1.0
        s = 0.5/math.sqrt(t)

        return cls(
          (m[1*4 + 2] - m[2*4 + 1])*s,
          s*t,
          (m[0*4 + 1] + m[1*4 + 0])*s,
          (m[2*4 + 0] + m[0*4 + 2])*s
          )

      elif m[1*4 + 1] > m[2*4 + 2]:
        t = -m[0*4 + 0] + m[1*4 + 1] - m[2*4 + 2] + 1.0
        s = 0.5/math.sqrt(t)

        return cls(
          (m[2*4 + 0] - m[0*4 + 2])*s,
          (m[0*4 + 1] + m[1*4 + 0])*s,
          s*t,
          (m[1*4 + 2] + m[2*4 + 1])*s
          )

      else:
        t = -m[0*4 + 0] - m[1*4 + 1] + m[2*4 + 2] + 1.0
        s = 0.5/math.sqrt(t)

        return cls(
          (m[0*4 + 1] - m[1*4 + 0])*s,
          (m[2*4 + 0] + m[0*4 + 2])*s,
          (m[1*4 + 2] + m[2*4 + 1])*s,
          s*t
          )

    @classmethod
    def interpolate(cls, q1, q2, t):
        assert isinstance(q1, Quaternion) and isinstance(q2, Quaternion)
        Q = cls()

        costheta = q1.w * q2.w + q1.x * q2.x + q1.y * q2.y + q1.z * q2.z
        if costheta < 0.:
            costheta = -costheta
            q1 = q1.conjugated()
        elif costheta > 1:
            costheta = 1

        theta = math.acos(costheta)
        if abs(theta) < 0.01:
            Q.w = q2.w
            Q.x = q2.x
            Q.y = q2.y
            Q.z = q2.z
            return Q

        sintheta = math.sqrt(1.0 - costheta * costheta)
        if abs(sintheta) < 0.01:
            Q.w = (q1.w + q2.w) * 0.5
            Q.x = (q1.x + q2.x) * 0.5
            Q.y = (q1.y + q2.y) * 0.5
            Q.z = (q1.z + q2.z) * 0.5
            return Q

        ratio1 = math.sin((1 - t) * theta) / sintheta
        ratio2 = math.sin(t * theta) / sintheta

        Q.w = q1.w * ratio1 + q2.w * ratio2
        Q.x = q1.x * ratio1 + q2.x * ratio2
        Q.y = q1.y * ratio1 + q2.y * ratio2
        Q.z = q1.z * ratio1 + q2.z * ratio2
        return Q

class Point(Vector, Geometry):
    """
    A close cousin of :py:class:`petrify.space.Vector`, used to represent a
    point instead of a transform.

    Defines a convenience `.origin` attribute for this commonly-used point:

    >>> Point.origin
    Point(0, 0, 0)

    """

    def __repr__(self):
        return 'Point({0!r}, {1!r}, {2!r})'.format(*self.xyz)

    def intersect(self, other):
        """
        Returns whether the point lies within the given `other` sphere:

        """
        return other._intersect_point3(self)

    def _intersect_sphere(self, other):
        return _intersect_point3_sphere(self, other)

    def connect(self, other):
        """
        Find the shortest line segment connecting this object to the `other`
        object.

        """
        return other._connect_point3(self)

    def _connect_point3(self, other):
        if self != other:
            return LineSegment(other, self)
        return None

    def _connect_line3(self, other):
        c = _connect_point3_line3(self, other)
        if c:
            return c._swap()

    def _connect_sphere(self, other):
        c = _connect_point3_sphere(self, other)
        if c:
            return c._swap()

    def _connect_plane(self, other):
        c = _connect_point3_plane(self, other)
        if c:
            return c._swap()

    def vector(self):
        """ The vector formed from the origin to this point. """
        return Vector(self.x, self.y, self.z)

Point.origin = Point(0, 0, 0)

class Line:
    """
    An infinite line:

    >>> Line(Point(0, 0, 0), Vector(1, 1, 1))
    Line(Point(0, 0, 0), Vector(1, 1, 1))
    >>> Line(Point(0, 0, 0), Point(1, 1, 1))
    Line(Point(0, 0, 0), Vector(1, 1, 1))

    """
    __slots__ = ['p', 'v']

    def __init__(self, *args):
        if len(args) == 3:
            assert isinstance(args[0], Point) and \
                   isinstance(args[1], Vector) and \
                   valid_scalar(args[2])
            self.p = args[0].copy()
            self.v = args[1] * args[2] / abs(args[1])
        elif len(args) == 2:
            if isinstance(args[0], Point) and isinstance(args[1], Point):
                self.p = args[0].copy()
                self.v = args[1] - args[0]
            elif isinstance(args[0], Point) and isinstance(args[1], Vector):
                self.p = args[0].copy()
                self.v = args[1].copy()
            else:
                raise AttributeError('%r' % (args,))
        elif len(args) == 1:
            if isinstance(args[0], Line):
                self.p = args[0].p.copy()
                self.v = args[0].v.copy()
            else:
                raise AttributeError('%r' % (args,))
        else:
            raise AttributeError('%r' % (args,))

        # XXX This is annoying.
        #if not self.v:
        #    raise AttributeError('Line has zero-length vector')

    def __copy__(self):
        return self.__class__(self.p, self.v)

    copy = __copy__

    def __repr__(self):
        return 'Line({0!r}, {1!r})'.format(self.p, self.v)

    p1 = property(lambda self: self.p)
    p2 = property(lambda self: Point(self.p.x + self.v.x,
                                      self.p.y + self.v.y,
                                      self.p.z + self.v.z))

    def _apply_transform(self, t):
        self.p = t * self.p
        self.v = t * self.v

    def _u_in(self, u):
        return True

    def intersect(self, other):
        """
        Find the point where this line intersects the `other` plane or sphere:

        >>> l = Line(Point(0, 0, 0), Vector(1, 1, 1));
        >>> p = Plane(Vector(0, 0, 1), 2);
        >>> l.intersect(p)
        Point(2.0, 2.0, 2.0)

        """
        return other._intersect_line3(self)

    def _intersect_sphere(self, other):
        return _intersect_line3_sphere(self, other)

    def _intersect_plane(self, other):
        return _intersect_line3_plane(self, other)

    def connect(self, other):
        """
        Find the shortest line segment connecting this object to the `other`
        object.

        """
        return other._connect_line3(self)

    def _connect_point3(self, other):
        return _connect_point3_line3(other, self)

    def _connect_line3(self, other):
        return _connect_line3_line3(other, self)

    def _connect_sphere(self, other):
        return _connect_sphere_line3(other, self)

    def _connect_plane(self, other):
        c = _connect_line3_plane(self, other)
        if c:
            return c

class Ray(Line):
    """
    A :py:class:`Line` with a fixed origin that continues indefinitely in the given
    direction.

    """
    def __repr__(self):
        return 'Ray({0!r}, {1!r})'.format(self.p, self.v)

    def _u_in(self, u):
        return u >= 0.0

class LineSegment(Line):
    def __repr__(self):
        return 'LineSegment({0!r}, {1!r})'.format(self.p, self.p2)

    def _u_in(self, u):
        return u >= 0.0 and u <= 1.0

    def __abs__(self):
        return abs(self.v)

    def magnitude_squared(self):
        return self.v.magnitude_squared()

    def _swap(self):
        # used by connect methods to switch order of points
        self.p = self.p2
        self.v *= -1
        return self

    def __eq__(self, other):
        if isinstance(other, LineSegment):
            return (
                (self.p1 == other.p1 and self.p2 == other.p2) or
                (self.p2 == other.p1 and self.p1 == other.p2)
            )
        raise RuntimeError("Cannot compute on: " + repr(other))

    def flipped(self):
        return LineSegment(self.p2, -self.v)

    def endpoints(self):
        return [self.p1, self.p2]

    def has_endpoint(self, p):
        return self.p1 == p or self.p2 == p

    def touches(self, other):
        if isinstance(other, Point):
            return self.has_endpoint(other)
        if isinstance(other, LineSegment):
            return self.has_endpoint(other.p1) or self.has_endpoint(other.p2)
        raise RuntimeError("Cannot compute on: " + repr(other))

    length = property(lambda self: abs(self.v))

class Sphere:
    """
    A perfect sphere with the provided `center` and `radius`:

    >>> Sphere(Point(0, 0, 0), 1.0)
    Sphere(Point(0, 0, 0), 1.0)

    """
    __slots__ = ['c', 'r']

    def __init__(self, center, radius):
        assert isinstance(center, Point) and valid_scalar(radius)
        self.c = center.copy()
        self.r = radius

    def __copy__(self):
        return self.__class__(self.c, self.r)

    copy = __copy__

    def __repr__(self):
        return 'Sphere({0!r}, {1})'.format(self.c, self.r)

    def _apply_transform(self, t):
        self.c = t * self.c

    def intersect(self, other):
        """
        Checks whether the `other` point lies within this sphere.

        """
        return other._intersect_sphere(self)

    def _intersect_point3(self, other):
        return _intersect_point3_sphere(other, self)

    def _intersect_line3(self, other):
        return _intersect_line3_sphere(other, self)

    def connect(self, other):
        """
        Find the shortest line segment connecting this object to the `other`
        object.

        """
        return other._connect_sphere(self)

    def _connect_point3(self, other):
        return _connect_point3_sphere(other, self)

    def _connect_line3(self, other):
        c = _connect_sphere_line3(self, other)
        if c:
            return c._swap()

    def _connect_sphere(self, other):
        return _connect_sphere_sphere(other, self)

    def _connect_plane(self, other):
        c = _connect_sphere_plane(self, other)
        if c:
            return c

class Plane:
    """
    A three-dimensional plane.

    Can be constructed with three coplanar points:

    >>> Plane(Point(0, 0, 0), Point(1, 0, 0), Point(0, 1, 0))
    Plane(Vector(0.0, 0.0, 1.0), 0.0)

    Or an origin point and two basis vectors:
    >>> Plane(Point(0, 0, 0), Vector.basis.x, Vector.basis.y)
    Plane(Vector(0.0, 0.0, 1.0), 0.0)

    Or a normal and solution scalar / point:

    >>> Plane(Vector.basis.z, 0)
    Plane(Vector(0.0, 0.0, 1.0), 0)
    >>> Plane(Vector.basis.z, Point.origin)
    Plane(Vector(0.0, 0.0, 1.0), 0.0)

    `Plane` also defines convenience methods for commonly used origin planes:

    >>> Plane.xy
    Plane(Vector(0.0, 0.0, 1.0), 0.0)
    >>> Plane.xz
    Plane(Vector(0.0, 1.0, 0.0), 0.0)
    >>> Plane.yz
    Plane(Vector(1.0, 0.0, 0.0), 0.0)

    """
    # n.p = k, where n is normal, p is point on plane, k is constant scalar
    __slots__ = ['n', 'k']

    def __init__(self, *args):
        if len(args) == 3:
            if isinstance(args[0], Point):
                if all(isinstance(a, Point) for a in args[1:]):
                    self.n = (args[1] - args[0]).cross(args[2] - args[0])
                    self.n.normalize()
                elif all(isinstance(a, Vector) for a in args[1:]):
                    self.n = args[1].cross(args[2])
                    self.n.normalize()
                else:
                    raise TypeError('Cannot instantiate Vector from {0!r}'.format(args))
                self.k = self.n.dot(args[0])
        elif len(args) == 2:
            if not isinstance(args[0], Vector):
                raise TypeError('Cannot instantiate Vector from {0!r}'.format(args))
            self.n = args[0].normalized()
            if isinstance(args[0], Vector) and isinstance(args[1], Point):
                self.k = self.n.dot(args[1])
            elif isinstance(args[0], Vector) and valid_scalar(args[1]):
                self.k = args[1]
            else:
                raise TypeError('Cannot instantiate Vector from {0!r}'.format(args))

        else:
            raise TypeError('Cannot instantiate Vector from {0!r}'.format(args))

        if not self.n:
            raise AttributeError('Points on plane are colinear')

    def __copy__(self):
        return self.__class__(self.n, self.k)

    copy = __copy__

    def __repr__(self):
        return 'Plane({0!r}, {1!r})'.format(self.n, self.k)

    def _get_point(self):
        # Return an arbitrary point on the plane
        if self.n.z:
            return Point(0., 0., self.k / self.n.z)
        elif self.n.y:
            return Point(0., self.k / self.n.y, 0.)
        else:
            return Point(self.k / self.n.x, 0., 0.)

    def _apply_transform(self, t):
        p = t * self._get_point()
        self.n = t * self.n
        self.k = self.n.dot(p)

    def intersect(self, other):
        """
        Find the point where this plane intersects the `other` line or plane:

        >>> Plane(Vector(0, 1, 0), 1).intersect(Plane(Vector(1, 0, 0), 2))
        Line(Point(2.0, 1.0, 0.0), Vector(0.0, 0.0, 1.0))
        >>> Plane(Vector(0, 0, 1), 2).intersect(Line(Point(0, 0, 0), Vector(1, 1, 1)))
        Point(2.0, 2.0, 2.0)

        """
        return other._intersect_plane(self)

    def _intersect_line3(self, other):
        return _intersect_line3_plane(other, self)

    def _intersect_plane(self, other):
        return _intersect_plane_plane(self, other)

    def connect(self, other):
        """
        Find the shortest line segment connecting this object to the `other`
        object.

        """
        return other._connect_plane(self)

    def _connect_point3(self, other):
        return _connect_point3_plane(other, self)

    def _connect_line3(self, other):
        return _connect_line3_plane(other, self)

    def _connect_sphere(self, other):
        return _connect_sphere_plane(other, self)

    def _connect_plane(self, other):
        return _connect_plane_plane(other, self)

    @property
    def normal(self): return self.n

Plane.xy = Plane(Vector(0.0, 0.0, 1.0), 0.0)
Plane.xz = Plane(Vector(0.0, 1.0, 0.0), 0.0)
Plane.yz = Plane(Vector(1.0, 0.0, 0.0), 0.0)

# 3D Geometry
# -------------------------------------------------------------------------

def _connect_point3_line3(P, L):
    d = L.v.magnitude_squared()
    assert d != 0
    u = ((P.x - L.p.x) * L.v.x + \
         (P.y - L.p.y) * L.v.y + \
         (P.z - L.p.z) * L.v.z) / d
    if not L._u_in(u):
        u = max(min(u, 1.0), 0.0)
    return LineSegment(P, Point(L.p.x + u * L.v.x,
                                  L.p.y + u * L.v.y,
                                  L.p.z + u * L.v.z))

def _connect_point3_sphere(P, S):
    v = P - S.c
    v.normalize()
    v *= S.r
    return LineSegment(P, Point(S.c.x + v.x, S.c.y + v.y, S.c.z + v.z))

def _connect_point3_plane(p, plane):
    n = plane.n.normalized()
    d = p.dot(plane.n) - plane.k
    return LineSegment(p, Point(p.x - n.x * d, p.y - n.y * d, p.z - n.z * d))

def _connect_line3_line3(A, B):
    assert A.v and B.v
    p13 = A.p - B.p
    d1343 = p13.dot(B.v)
    d4321 = B.v.dot(A.v)
    d1321 = p13.dot(A.v)
    d4343 = B.v.magnitude_squared()
    denom = A.v.magnitude_squared() * d4343 - d4321 ** 2
    if denom == 0:
        # Parallel, connect an endpoint with a line
        if isinstance(B, Ray) or isinstance(B, LineSegment):
            return _connect_point3_line3(B.p, A)._swap()
        # No endpoint (or endpoint is on A), possibly choose arbitrary
        # point on line.
        return _connect_point3_line3(A.p, B)

    ua = (d1343 * d4321 - d1321 * d4343) / denom
    if not A._u_in(ua):
        ua = max(min(ua, 1.0), 0.0)
    ub = (d1343 + d4321 * ua) / d4343
    if not B._u_in(ub):
        ub = max(min(ub, 1.0), 0.0)
    return LineSegment(Point(A.p.x + ua * A.v.x,
                               A.p.y + ua * A.v.y,
                               A.p.z + ua * A.v.z),
                        Point(B.p.x + ub * B.v.x,
                               B.p.y + ub * B.v.y,
                               B.p.z + ub * B.v.z))

def _connect_line3_plane(L, P):
    d = P.n.dot(L.v)
    if not d:
        # Parallel, choose an endpoint
        return _connect_point3_plane(L.p, P)
    u = (P.k - P.n.dot(L.p)) / d
    if not L._u_in(u):
        # intersects out of range, choose nearest endpoint
        u = max(min(u, 1.0), 0.0)
        return _connect_point3_plane(Point(L.p.x + u * L.v.x,
                                            L.p.y + u * L.v.y,
                                            L.p.z + u * L.v.z), P)
    # Intersection
    return None

def _connect_sphere_line3(S, L):
    d = L.v.magnitude_squared()
    assert d != 0
    u = ((S.c.x - L.p.x) * L.v.x + \
         (S.c.y - L.p.y) * L.v.y + \
         (S.c.z - L.p.z) * L.v.z) / d
    if not L._u_in(u):
        u = max(min(u, 1.0), 0.0)
    point = Point(L.p.x + u * L.v.x, L.p.y + u * L.v.y, L.p.z + u * L.v.z)
    v = (point - S.c)
    v.normalize()
    v *= S.r
    return LineSegment(Point(S.c.x + v.x, S.c.y + v.y, S.c.z + v.z),
                        point)

def _connect_sphere_sphere(A, B):
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

    v.normalize()
    return LineSegment(Point(A.c.x + s1* v.x * A.r,
                               A.c.y + s1* v.y * A.r,
                               A.c.z + s1* v.z * A.r),
                        Point(B.c.x + s2* v.x * B.r,
                               B.c.y + s2* v.y * B.r,
                               B.c.z + s2* v.z * B.r))

def _connect_sphere_plane(S, P):
    c = _connect_point3_plane(S.c, P)
    if not c:
        return None
    p2 = c.p2
    v = p2 - S.c
    v.normalize()
    v *= S.r
    return LineSegment(Point(S.c.x + v.x, S.c.y + v.y, S.c.z + v.z),
                        p2)

def _connect_plane_plane(A, B):
    if A.n.cross(B.n):
        # Planes intersect
        return None
    else:
        # Planes are parallel, connect to arbitrary point
        return _connect_point3_plane(A._get_point(), B)

def _intersect_point3_sphere(P, S):
    return abs(P - S.c) <= S.r

def _intersect_line3_sphere(L, S):
    a = L.v.magnitude_squared()
    b = 2 * (L.v.x * (L.p.x - S.c.x) + \
             L.v.y * (L.p.y - S.c.y) + \
             L.v.z * (L.p.z - S.c.z))
    c = S.c.magnitude_squared() + \
        L.p.magnitude_squared() - \
        2 * S.c.dot(L.p) - \
        S.r ** 2
    det = b ** 2 - 4 * a * c
    if det < 0:
        return None
    sq = math.sqrt(det)
    u1 = (-b + sq) / (2 * a)
    u2 = (-b - sq) / (2 * a)
    if not L._u_in(u1):
        u1 = max(min(u1, 1.0), 0.0)
    if not L._u_in(u2):
        u2 = max(min(u2, 1.0), 0.0)
    return LineSegment(Point(L.p.x + u1 * L.v.x,
                               L.p.y + u1 * L.v.y,
                               L.p.z + u1 * L.v.z),
                        Point(L.p.x + u2 * L.v.x,
                               L.p.y + u2 * L.v.y,
                               L.p.z + u2 * L.v.z))

def _intersect_line3_plane(L, P):
    d = P.n.dot(L.v)
    if not d:
        # Parallel
        return None
    u = (P.k - P.n.dot(L.p)) / d
    if not L._u_in(u):
        return None
    return Point(L.p.x + u * L.v.x,
                  L.p.y + u * L.v.y,
                  L.p.z + u * L.v.z)

def _intersect_plane_plane(A, B):
    n1_m = A.n.magnitude_squared()
    n2_m = B.n.magnitude_squared()
    n1d2 = A.n.dot(B.n)
    det = n1_m * n2_m - n1d2 ** 2
    if det == 0:
        # Parallel
        return None
    c1 = (A.k * n2_m - B.k * n1d2) / det
    c2 = (B.k * n1_m - A.k * n1d2) / det
    return Line(Point(c1 * A.n.x + c2 * B.n.x,
                        c1 * A.n.y + c2 * B.n.y,
                        c1 * A.n.z + c2 * B.n.z),
                 A.n.cross(B.n))
