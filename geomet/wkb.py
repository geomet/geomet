import struct
import binascii
from itertools import chain

from geomet.util import block_splitter

#: '\x00': The first byte of any WKB string. Indicates big endian byte
#: ordering for the data.
BIG_ENDIAN = b'\x00'
#: '\x01': The first byte of any WKB string. Indicates little endian byte
#: ordering for the data.
LITTLE_ENDIAN = b'\x01'

#: Mapping of GeoJSON geometry types to the "2D" 4-byte binary string
#: representation for WKB. "2D" indicates that the geometry is 2-dimensional,
#: X and Y components.
#: NOTE: Byte ordering is big endian.
WKB_2D = {
    'Point': b'\x00\x00\x00\x01',
    'LineString': b'\x00\x00\x00\x02',
    'Polygon': b'\x00\x00\x00\x03',
    'MultiPoint': b'\x00\x00\x00\x04',
    'MultiLineString': b'\x00\x00\x00\x05',
    'MultiPolygon': b'\x00\x00\x00\x06',
    'GeometryCollection': b'\x00\x00\x00\x07',
}

#: Mapping of GeoJSON geometry types to the "Z" 4-byte binary string
#: representation for WKB. "Z" indicates that the geometry is 3-dimensional,
#: with X, Y, and Z components.
#: NOTE: Byte ordering is big endian.
WKB_Z = {
    'Point': b'\x00\x00\x10\x01',
    'LineString': b'\x00\x00\x10\x02',
    'Polygon': b'\x00\x00\x10\x03',
    'MultiPoint': b'\x00\x00\x10\x04',
    'MultiLineString': b'\x00\x00\x10\x05',
    'MultiPolygon': b'\x00\x00\x10\x06',
    'GeometryCollection': b'\x00\x00\x10\x07',
}

#: Mapping of GeoJSON geometry types to the "M" 4-byte binary string
#: representation for WKB. "M" indicates that the geometry is 2-dimensional,
#: with X, Y, and M ("Measure") components.
#: NOTE: Byte ordering is big endian.
WKB_M = {
    'Point': b'\x00\x00\x20\x01',
    'LineString': b'\x00\x00\x20\x02',
    'Polygon': b'\x00\x00\x20\x03',
    'MultiPoint': b'\x00\x00\x20\x04',
    'MultiLineString': b'\x00\x00\x20\x05',
    'MultiPolygon': b'\x00\x00\x20\x06',
    'GeometryCollection': b'\x00\x00\x20\x07',
}

#: Mapping of GeoJSON geometry types to the "ZM" 4-byte binary string
#: representation for WKB. "ZM" indicates that the geometry is 4-dimensional,
#: with X, Y, Z, and M ("Measure") components.
#: NOTE: Byte ordering is big endian.
WKB_ZM = {
    'Point': b'\x00\x00\x30\x01',
    'LineString': b'\x00\x00\x30\x02',
    'Polygon': b'\x00\x00\x30\x03',
    'MultiPoint': b'\x00\x00\x30\x04',
    'MultiLineString': b'\x00\x00\x30\x05',
    'MultiPolygon': b'\x00\x00\x30\x06',
    'GeometryCollection': b'\x00\x00\x30\x07',
}

#: Mapping of dimension types to maps of GeoJSON geometry type -> 4-byte binary
#: string representation for WKB.
__WKB = {
    '2D': WKB_2D,
    'Z': WKB_Z,
    'M': WKB_M,
    'ZM': WKB_ZM,
}

#: Mapping from binary geometry type (as a 4-byte binary string) to GeoJSON
#: geometry type.
#: NOTE: Byte ordering is big endian.
__BINARY_TO_GEOM_TYPE = dict(
    chain(*((reversed(x) for x in wkb_map.items())
            for wkb_map in __WKB.values()))
)


def dump(obj, dest_file):
    """
    Dump GeoJSON-like `dict` to WKB and write it to the `dest_file`.

    :param dict obj:
        A GeoJSON-like dictionary. It must at least the keys 'type' and
        'coordinates'.
    :param dest_file:
        Open and writable file-like object.
    """
    dest_file.write(dumps(obj))


def load(source_file):
    """
    Load a GeoJSON `dict` object from a ``source_file`` containing WKB (as a
    byte string).

    :param source_file:
        Open and readable file-like object.

    :returns:
        A GeoJSON `dict` representing the geometry read from the file.
    """
    return loads(source_file.read())


def dumps(obj, big_endian=True):
    """
    Dump a GeoJSON-like `dict` to a WKB string.

    .. note::
        The dimensions of the generated WKB will be inferred from the first
        vertex in the GeoJSON `coordinates`. It will be assumed that all
        vertices are uniform. There are 4 types:

        - 2D (X, Y): 2-dimensional geometry
        - Z (X, Y, Z): 3-dimensional geometry
        - M (X, Y, M): 2-dimensional geometry with a "Measure"
        - ZM (X, Y, Z, M): 3-dimensional geometry with a "Measure"

        If the first vertex contains 2 values, we assume a 2D geometry.
        If the first vertex contains 3 values, this is slightly ambiguous and
        so the most common case is chosen: Z.
        If the first vertex contains 4 values, we assume a ZM geometry.

        The WKT/WKB standards provide a way of differentiating normal (2D), Z,
        M, and ZM geometries (http://en.wikipedia.org/wiki/Well-known_text),
        but the GeoJSON spec does not. Therefore, for the sake of interface
        simplicity, we assume that geometry that looks 3D contains XYZ
        components, instead of XYM.

    :param dict obj:
        GeoJson-like `dict` object.
    :param bool big_endian:
        Defaults to `True`. If `True`, data values in the generated WKB will
        be represented using big endian byte order. Else, little endian.
    :param str dims:
        Indicates to WKB representation desired from converting the given
        GeoJSON `dict` ``obj``. The accepted values are:

        * '2D': 2-dimensional geometry (X, Y)
        * 'Z': 3-dimensional geometry (X, Y, Z)
        * 'M': 3-dimensional geometry (X, Y, M)
        * 'ZM': 4-dimensional geometry (X, Y, Z, M)

    :returns:
        A WKB binary string representing of the ``obj``.
    """
    geom_type = obj['type']

    exporter = __dumps_registry.get(geom_type)
    if exporter is None:
        __unsupported_geom_type(geom_type)

    return exporter(obj, big_endian)


def loads(string):
    """
    Construct a GeoJson `dict` from WKB (`string`).
    """
    endianness = string[0:1]
    if endianness == BIG_ENDIAN:
        big_endian = True
    elif endianness == LITTLE_ENDIAN:
        big_endian = False
    else:
        raise ValueError("Invalid endian byte: '0x%s'. Expected 0x00 or 0x01"
                         % binascii.hexlify(endianness.encode()).decode())

    type_bytes = string[1:5]
    if not big_endian:
        # To identify the type, order the type bytes in big endian:
        type_bytes = type_bytes[::-1]

    geom_type = __BINARY_TO_GEOM_TYPE.get(type_bytes)
    data_bytes = string[5:]  # FIXME: This won't work for GeometryCollections

    importer = __loads_registry.get(geom_type)

    if importer is None:
        __unsupported_geom_type(geom_type)
    return importer(big_endian, type_bytes, data_bytes)


def __unsupported_geom_type(geom_type):
    raise ValueError("Unsupported geometry type '%s'" % geom_type)


def __dump_point(obj, big_endian):
    """
    Dump a GeoJSON-like `dict` to a point WKB string.

    :param dict obj:
        GeoJson-like `dict` object.
    :param bool big_endian:
        If `True`, data values in the generated WKB will be represented using
        big endian byte order. Else, little endian.

    :returns:
        A WKB binary string representing of the Point ``obj``.
    """
    wkb_string = b''

    if big_endian:
        wkb_string += BIG_ENDIAN
        byte_fmt = '>'
    else:
        wkb_string += LITTLE_ENDIAN
        byte_fmt = '<'

    coords = obj['coordinates']
    num_dims = len(coords)
    if num_dims == 2:
        type_byte_str = __WKB['2D']['Point']
    elif num_dims == 3:
        type_byte_str = __WKB['Z']['Point']
    elif num_dims == 4:
        type_byte_str = __WKB['ZM']['Point']
    else:
        pass
        # TODO: raise

    if not big_endian:
        # reverse the byte ordering for little endian
        type_byte_str = type_byte_str[::-1]
    wkb_string += type_byte_str

    byte_fmt += 'd' * num_dims

    wkb_string += struct.pack(byte_fmt, *coords)
    return wkb_string


def __dump_linestring(obj, big_endian):
    """
    Dump a GeoJSON-like `dict` to a linestring WKB string.

    Input parameters and output are similar to :func:`__dump_point`.
    """
    wkb_string = b''

    if big_endian:
        wkb_string += BIG_ENDIAN
        byte_fmt = '>'
    else:
        wkb_string += LITTLE_ENDIAN
        byte_fmt = '<'

    coords = obj['coordinates']
    vertex = coords[0]
    # Infer the number of dimensions from the first vertex
    num_dims = len(vertex)
    if num_dims == 2:
        type_byte_str = __WKB['2D']['LineString']
    elif num_dims == 3:
        type_byte_str = __WKB['Z']['LineString']
    elif num_dims == 4:
        type_byte_str = __WKB['ZM']['LineString']
    else:
        pass
        # TODO: raise
    if not big_endian:
        # reverse the byte ordering for little endian
        type_byte_str = type_byte_str[::-1]
    wkb_string += type_byte_str

    byte_fmt += 'd' * num_dims

    for vertex in coords:
        wkb_string += struct.pack(byte_fmt, *vertex)

    return wkb_string


def __dump_polygon(obj, big_endian):
    """
    Dump a GeoJSON-like `dict` to a polygon WKB string.

    Input parameters and output are similar to :funct:`__dump_point`.
    """
    wkb_string = b''

    if big_endian:
        wkb_string += BIG_ENDIAN
        end_fmt = '>'
    else:
        wkb_string += LITTLE_ENDIAN
        end_fmt = '<'

    coords = obj['coordinates']
    vertex = coords[0][0]
    # Infer the number of dimensions from the first vertex
    num_dims = len(vertex)
    if num_dims == 2:
        type_byte_str = __WKB['2D']['Polygon']
    elif num_dims == 3:
        type_byte_str = __WKB['Z']['Polygon']
    elif num_dims == 4:
        type_byte_str = __WKB['ZM']['Polygon']
    else:
        pass
        # TODO: raise
    if not big_endian:
        # reverse the byte ordering for little endian
        type_byte_str = type_byte_str[::-1]
    wkb_string += type_byte_str

    byte_fmt = end_fmt + 'd' * num_dims

    # number of rings:
    wkb_string += struct.pack('%sl' % end_fmt, len(coords))
    for ring in coords:
        # number of verts in this ring:
        wkb_string += struct.pack('%sl' % end_fmt, len(ring))
        for vertex in ring:
            wkb_string += struct.pack(byte_fmt, *vertex)

    return wkb_string


__dumps_registry = {
    'Point': __dump_point,
    'LineString': __dump_linestring,
    'Polygon': __dump_polygon,
}


def __load_point(big_endian, type_bytes, data_bytes):
    """
    Convert byte data for a Point to a GeoJSON `dict`.

    :param bool big_endian:
        If `True`, interpret the ``data_bytes`` in big endian order, else
        little endian.
    :param str type_bytes:
        4-byte integer (as a binary string) indicating the geometry type
        (Point) and the dimensions (2D, Z, M or ZM). For consistency, these
        bytes are expected to always be in big endian order, regardless of the
        value of ``big_endian``.
    :param str data_bytes:
        Coordinate data in a binary string.

    :returns:
        GeoJSON `dict` representing the Point geometry.
    """
    endian_token = '>' if big_endian else '<'

    if type_bytes == WKB_2D['Point']:
        coords = struct.unpack('%sdd' % endian_token, data_bytes)
    elif type_bytes == WKB_Z['Point']:
        coords = struct.unpack('%sddd' % endian_token, data_bytes)
    elif type_bytes == WKB_M['Point']:
        # NOTE: The use of XYM types geometries is quite rare. In the interest
        # of removing ambiguity, we will treat all XYM geometries as XYZM when
        # generate the GeoJSON. A default Z value of `0.0` will be given in
        # this case.
        coords = list(struct.unpack('%sddd' % endian_token, data_bytes))
        coords.insert(2, 0.0)
    elif type_bytes == WKB_ZM['Point']:
        coords = struct.unpack('%sdddd' % endian_token, data_bytes)

    return dict(type='Point', coordinates=list(coords))


def __load_linestring(big_endian, type_bytes, data_bytes):
    endian_token = '>' if big_endian else '<'

    num_vals = int(len(data_bytes) / 8)  # 8 bytes per float val
    values = struct.unpack('%s%s' % (endian_token, 'd' * num_vals),
                           data_bytes)

    if type_bytes == WKB_2D['LineString']:
        coords = block_splitter(values, 2)
    elif type_bytes == WKB_Z['LineString']:
        coords = block_splitter(values, 3)
    elif type_bytes == WKB_M['LineString']:
        coords = block_splitter(values, 3)
        # For the M type geometry, insert values of 0.0 for Z
        # This effectively converts a M type geometry into a ZM.
        coords = ([x, y, 0.0, m] for x, y, m in coords)
    elif type_bytes == WKB_ZM['LineString']:
        coords = block_splitter(values, 4)

    return dict(type='LineString', coordinates=list(coords))


__loads_registry = {
    'Point': __load_point,
    'LineString': __load_linestring,
}
