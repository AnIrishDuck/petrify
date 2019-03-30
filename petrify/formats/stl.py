import struct
from csg.geom import Polygon, Vertex

from ..solid import from_pycsg, Node
from .. import units

class STL:
    """
    A STL-formatted file at the given `path` with the specified file `scale`:

    >>> import tempfile
    >>> from petrify import u
    >>> output = STL.read('tests/fixtures/svg.stl', 1 * u.mm / u.file)
    >>> output = STL.read('tests/fixtures/svg.stl', 'mm')
    >>> with tempfile.NamedTemporaryFile() as fp: \
        STL(fp.name, 'inches').write(output)

    """
    def __init__(self, path, scale):
        self.path = path
        self.scale = units.conversion(scale)

    @classmethod
    def read(cls, path, scale):
        """
        Read a :class:`petrify.solid.Node` from a STL-formatted file:

        >>> from petrify import u
        >>> e = STL.read('tests/fixtures/svg.stl', 1 * u.inch / u.file)
        >>> len(e.polygons)
        40
        >>> e.units
        <Unit('inch')>

        """
        polygons = read_polys_from_stl_file(path)
        scale = units.conversion(scale)
        return Node(from_pycsg(polygons)) * units.u.file * scale

    def write(self, solid):
        """
        Save a :class:`petrify.solid.Node` to a STL-formatted file.

        >>> from petrify import u
        >>> from petrify.solid import Box, Point, Vector
        >>> b = Box(Point.origin, Vector(1, 1, 1))
        >>> STL('tests/fixtures/svg.stl', 1 * u.mm / u.file).write(b.as_unit('inches'))

        The input geometry must have a length unit tag:

        >>> STL('tests/fixtures/svg.stl', 1 * u.mm / u.file).write(b)
        Traceback (most recent call last):
        ...
        AssertionError: object does not have unit tag: Box(Point(0, 0, 0), Vector(1, 1, 1))

        """
        units.assert_lengthy(solid)
        output = (solid / self.scale).m_as(units.u.file)
        save_polys_to_stl_file(output.pycsg.toPolygons(), self.path)

class StlEndOfFileException(Exception):
    """Exception class for reaching the end of the STL file while reading."""
    pass


class StlMalformedLineException(Exception):
    """Exception class for malformed lines in the STL file being read."""
    pass


def _float_fmt(val):
    """
    Make a short, clean, string representation of a float value.
    """
    s = ("%.6f" % val).rstrip('0').rstrip('.')
    return '0' if s == '-0' else s


def _stl_write_facet(poly, f, binary=True):
    """
    Writes a single triangle facet to the given STL file stream.
    binary - Save in binary format if True, else ASCII format.
    """
    norm = poly.plane.normal
    v0, v1, v2 = poly.vertices
    if binary:
        data = struct.pack(
            '<3f 3f 3f 3f H',
            norm[0], norm[1], norm[2],
            v0.pos[0], v0.pos[1], v0.pos[2],
            v1.pos[0], v1.pos[1], v1.pos[2],
            v2.pos[0], v2.pos[1], v2.pos[2],
            0
        )
        f.write(data)
    else:
        v0 = " ".join(_float_fmt(x) for x in v0.pos)
        v1 = " ".join(_float_fmt(x) for x in v1.pos)
        v2 = " ".join(_float_fmt(x) for x in v2.pos)
        norm = " ".join(_float_fmt(x) for x in norm)
        vfmt = (
            "  facet normal {norm}\n"
            "    outer loop\n"
            "      vertex {v0}\n"
            "      vertex {v1}\n"
            "      vertex {v2}\n"
            "    endloop\n"
            "  endfacet\n"
        )
        data = vfmt.format(norm=norm, v0=v0, v1=v1, v2=v2)
        f.write(bytes(data, encoding='ascii'))


def save_polys_to_stl_file(polys, filename, binary=True):
    """
    Save polygons in STL file.
    polys - list of Polygons.
    filename - Name fo the STL file to save to.
    binary - if true (default), file is written in binary STL format.  Otherwise ASCII STL format.
    """
    # Convert all polygons to triangles.
    tris = []
    for poly in polys:
        vlen = len(poly.vertices)
        for n in range(1,vlen-1):
            tris.append(
                Polygon([
                    poly.vertices[0],
                    poly.vertices[n%vlen],
                    poly.vertices[(n+1)%vlen],
                ])
            )
    if binary:
        with open(filename, 'wb') as f:
            f.write(b'%-80s' % b'Binary STL Model')
            f.write(struct.pack('<I', len(tris)))
            for tri in tris:
                _stl_write_facet(tri, f, binary=binary)
    else:
        with open(filename, 'wb') as f:
            f.write(b"solid Model\n")
            for tri in tris:
                _stl_write_facet(tri, f, binary=binary)
            f.write(b"endsolid Model\n")


def _read_ascii_line(f, watchwords=None):
    """
    Reads a single line from an ASCII STL file stream and checks for required keywords.
    Returns array of float values from the read line.
    Throws StlEndOfFileException if 'endsolid' line is read.
    Throws StlMalformedLineException if keywords are not found.
    """
    line = f.readline(1024).decode("ascii")
    if line == "":
        raise StlEndOfFileException()
    words = line.strip(' \t\n\r').lower().split()
    if words[0] == 'endsolid':
        raise StlEndOfFileException()
    argstart = 0
    if watchwords:
        watchwords = watchwords.lower().split()
        argstart = len(watchwords)
        for i in range(argstart):
            if words[i] != watchwords[i]:
                raise StlMalformedLineException()
    return [float(val) for val in words[argstart:]]


def _read_ascii_facet(f):
    """
    Load a single facet triangle from the ASCII STL file stream.
    Skips corrupted facets if it can.
    Returns a Polygon.
    Throws StlEndOfFileException if EOF is reached.
    """
    while True:
        try:
            normal = _read_ascii_line(f, watchwords='facet normal')
            _read_ascii_line(f, watchwords='outer loop')
            v0 = _read_ascii_line(f, watchwords='vertex')
            v1 = _read_ascii_line(f, watchwords='vertex')
            v2 = _read_ascii_line(f, watchwords='vertex')
            _read_ascii_line(f, watchwords='endloop')
            _read_ascii_line(f, watchwords='endfacet')
            if v0 == v1 or v1 == v2 or v2 == v0:
                continue  # zero area facet.  Skip to next facet.
        except StlEndOfFileException:
            return None
        except StlMalformedLineException:
            continue  # Skip to next facet.
        v0 = Vertex(v0)
        v1 = Vertex(v1)
        v2 = Vertex(v2)
        return Polygon([v0, v1, v2])


def _read_binary_facet(f):
    """
    Load a single facet triangle from the binary STL file stream.
    Returns a Polygon.
    """
    data = struct.unpack('<3f 3f 3f 3f H', f.read(4*4*3+2))
    normal = data[0:3]
    v0 = Vertex(data[3:6])
    v1 = Vertex(data[6:9])
    v2 = Vertex(data[9:12])
    return Polygon([v0, v1, v2])


def read_polys_from_stl_file(filename):
    """
    Read array of triangle polygons from an STL file.
    filename - Name fo the STL file to read from.
    """
    polygons = []
    with open(filename, 'rb') as f:
        line = f.readline(80)
        if line == "":
            return  # End of file.
        line = line.lstrip()
        if line[0:6].lower() == b"solid ":
            # Reading ASCII STL file.
            while True:
                poly = _read_ascii_facet(f)
                if not poly:
                    break
                polygons.append(poly)
        else:
            # Reading Binary STL file.
            chunk = f.read(4)
            facets = struct.unpack('<I', chunk)[0]
            for n in range(facets):
                poly = _read_binary_facet(f)
                if not poly:
                    break
                polygons.append(poly)
    return polygons
