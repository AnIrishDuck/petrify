from ..geometry import tau
import math

# a b c d
# e f g h
# i j k l
# m n o p
class Matrix3:
    """
    A matrix that can be used to perform common transformations on
    three-dimensional points and vectors:

    >>> from . import Point, Vector
    >>> Matrix3.scale(*Vector(1, 2, 1).xyz) * Point(1, 1, 1)
    Point(1, 2, 1)

    """
    __slots__ = list('abcdefghijklmnop')

    def __init__(self):
        self.a = self.f = self.k = self.p = 1.
        self.b = self.c = self.d = self.e = self.g = self.h = \
        self.i = self.j = self.l = self.m = self.n = self.o = 0

    def __copy__(self):
        M = Matrix3()
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
        return ('Matrix3([% 8.2f % 8.2f % 8.2f % 8.2f\n'  \
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
        from . import Point3, Vector3
        if isinstance(other, Matrix3):
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
            C = Matrix3()
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
        elif isinstance(other, Point3):
            A = self
            B = other
            P = Point3(0, 0, 0)
            P.x = A.a * B.x + A.b * B.y + A.c * B.z + A.d
            P.y = A.e * B.x + A.f * B.y + A.g * B.z + A.h
            P.z = A.i * B.x + A.j * B.y + A.k * B.z + A.l
            return P
        elif isinstance(other, Vector3):
            A = self
            B = other
            V = Vector3(0, 0, 0)
            V.x = A.a * B.x + A.b * B.y + A.c * B.z
            V.y = A.e * B.x + A.f * B.y + A.g * B.z
            V.z = A.i * B.x + A.j * B.y + A.k * B.z
            return V
        else:
            other = other.copy()
            other._apply_transform(self)
            return other
    __rmul__ = __mul__

    def __imul__(self, other):
        assert isinstance(other, Matrix3)
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
        P = Point3(0, 0, 0)
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

        >>> from . import Point
        >>> Matrix3.identity() * Point(1, 1, 1)
        Point(1.0, 1.0, 1.0)

        """
        self = cls()
        return self

    @classmethod
    def scale(cls, x, y, z):
        """
        A scale transform:

        >>> from . import Point, Vector
        >>> Matrix3.scale(*Vector(1, 2, 1).xyz) * Point(1, 1, 1)
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

        >>> from . import Point, Vector
        >>> Matrix3.translate(*Vector(1, 2, 1).xyz) * Point(1, 1, 1)
        Point(2.0, 3.0, 2.0)

        """
        self = cls()
        self.d = x
        self.h = y
        self.l = z
        return self

    @classmethod
    def rotate_axis(cls, axis, angle):
        """
        A rotational transform:

        >>> from . import Point, Vector
        >>> (Matrix3.rotate_axis(Vector.basis.z, tau / 4) * Point(1, 0, 0)).rounded()
        Point(0, 1, 0)

        """
        from . import Vector3
        assert(isinstance(axis, Vector3))
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
    def rotate_at(cls, origin, axis, angle):
        """
        A rotational transform:

        >>> from . import Point, Vector
        >>> rotation = Matrix3.rotate_at(Point(1, 1, 1), Vector.basis.z, tau / 4)
        >>> (rotation * Point(2, 1, 1)).rounded()
        Point(1, 2, 1)

        """
        return (
            Matrix3.translate(*(origin).xyz) *
            Matrix3.rotate_axis(axis, angle) *
            Matrix3.translate(*(-origin).xyz)
        )

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
        tmp = Matrix3()
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
Matrix = Matrix3

class Quaternion:
    """
    Quaternions are composable representations of three-dimensional rotation
    operations.

    Multiplication can be performed on `Vector` instances to get the transformed
    vector or point:

    >>> from . import Vector
    >>> r = Quaternion.rotate_axis(Vector.basis.x, tau / 4);
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
        from . import Point3, Vector3
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
        elif isinstance(other, Vector3):
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

    def rotate_axis(self, axis, angle):
        self *= Quaternion.rotate_axis(axis, angle)
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
            return angle, Vector3(1, 0, 0)
        else:
            return angle, Vector3(self.x / s, self.y / s, self.z / s)

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
        M = Matrix3()
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
    def rotate_axis(cls, axis, angle):
        from . import Vector3
        assert(isinstance(axis, Vector3))
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
