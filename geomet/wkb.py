import struct
from itertools import chain

#: '\x00': The first byte of any WKB string. Indicates big endian byte
#: ordering for the data.
BIG_ENDIAN = '\x00'
#: '\x01': The first byte of any WKB string. Indicates little endian byte
#: ordering for the data.
LITTLE_ENDIAN = '\x01'

#: Mapping of GeoJSON geometry types to the "2D" 4-byte binary string
#: representation for WKB. "2D" indicates that the geometry is 2-dimensional,
#: X and Y components.
#: NOTE: Byte ordering is big endian.
WKB_2D = {
    'Point': '\x00\x00\x00\x01',
    'LineString': '\x00\x00\x00\x02',
    'Polygon': '\x00\x00\x00\x03',
    'MultiPoint': '\x00\x00\x00\x04',
    'MultiLineString': '\x00\x00\x00\x05',
    'MultiPolygon': '\x00\x00\x00\x06',
    'GeometryCollection': '\x00\x00\x00\x07',
}

#: Mapping of GeoJSON geometry types to the "Z" 4-byte binary string
#: representation for WKB. "Z" indicates that the geometry is 3-dimensional,
#: with X, Y, and Z components.
#: NOTE: Byte ordering is big endian.
WKB_Z = {
    'Point': '\x00\x00\x10\x01',
    'LineString': '\x00\x00\x10\x02',
    'Polygon': '\x00\x00\x10\x03',
    'MultiPoint': '\x00\x00\x10\x04',
    'MultiLineString': '\x00\x00\x10\x05',
    'MultiPolygon': '\x00\x00\x10\x06',
    'GeometryCollection': '\x00\x00\x10\x07',
}

#: Mapping of GeoJSON geometry types to the "M" 4-byte binary string
#: representation for WKB. "M" indicates that the geometry is 2-dimensional,
#: with X, Y, and M ("Measure") components.
#: NOTE: Byte ordering is big endian.
WKB_M = {
    'Point': '\x00\x00\x20\x01',
    'LineString': '\x00\x00\x20\x02',
    'Polygon': '\x00\x00\x20\x03',
    'MultiPoint': '\x00\x00\x20\x04',
    'MultiLineString': '\x00\x00\x20\x05',
    'MultiPolygon': '\x00\x00\x20\x06',
    'GeometryCollection': '\x00\x00\x20\x07',
}

#: Mapping of GeoJSON geometry types to the "ZM" 4-byte binary string
#: representation for WKB. "ZM" indicates that the geometry is 4-dimensional,
#: with X, Y, Z, and M ("Measure") components.
#: NOTE: Byte ordering is big endian.
WKB_ZM = {
    'Point': '\x00\x00\x30\x01',
    'LineString': '\x00\x00\x30\x02',
    'Polygon': '\x00\x00\x30\x03',
    'MultiPoint': '\x00\x00\x30\x04',
    'MultiLineString': '\x00\x00\x30\x05',
    'MultiPolygon': '\x00\x00\x30\x06',
    'GeometryCollection': '\x00\x00\x30\x07',
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
    chain(*((reversed(x) for x in wkb_map.iteritems())
            for wkb_map in __WKB.values()))
)


def dump(obj, dest_file):
    raise NotImplementedError


def load(source_file):
    raise NotImplementedError


def dumps(obj, big_endian=True, dims='2D'):
    """
    Dump a GeoJSON-like `dict` to a WKB string.

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

    mapping = __WKB.get(dims)
    if mapping is None:
        raise ValueError('Invalid `dims` type. Expected: one of %s. Got: %s'
                         % (('2D', 'Z', 'M', 'ZM'), dims))

    if dims == '2D':
        num_dims = 2
        mapping = WKB_2D
    elif dims in ('Z', 'M'):
        num_dims = 3
    elif dims == 'ZM':
        num_dims = 4

    type_byte_str = mapping.get(geom_type)
    if not big_endian:
        # reverse the byte ordering for little endian
        type_byte_str = type_byte_str[::-1]

    return exporter(obj, big_endian, type_byte_str, num_dims)


def loads(string):
    """
    Construct a GeoJson `dict` from WKB (`string`).
    """
    endianness = string[0]
    if endianness == BIG_ENDIAN:
        big_endian = True
    elif endianness == LITTLE_ENDIAN:
        big_endian = False
    else:
        raise ValueError("Invalid endian byte: '0x%s'. Expected 0x00 or 0x01"
                         % endianness.encode('hex'))

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


def __dump_point(obj, big_endian, type_byte_str, num_dims):
    """
    Dump a GeoJSON-like `dict` to a WKB string.

    :param dict obj:
        GeoJson-like `dict` object.
    :param bool big_endian:
        If `True`, data values in the generated WKB will be represented using
        big endian byte order. Else, little endian.
    :param str type_byte_str:
        The binary string representation of this type of geometry. Indicates
        not only the type (point, linestring, etc.) but also the dimension type
        (2D, Z, M, ZM).
    :param int num_dims:
        The number of dimensions in each vertex: 2, 3, or 4.

    :returns:
        A WKB binary string representing of the Point ``obj``.
    """
    wkb_string = ''

    if big_endian:
        wkb_string += BIG_ENDIAN
    else:
        wkb_string += LITTLE_ENDIAN

    wkb_string += type_byte_str

    coords = obj['coordinates']
    num_coord_dims = len(coords)
    if not len(coords) == num_dims:
        raise ValueError(
            'Incorrect number of dimension. Expected: %s. Got: %s'
            % (num_dims, num_coord_dims)
        )

    byte_fmt = ''
    if big_endian:
        byte_fmt += '>'
    else:
        byte_fmt += '<'
    byte_fmt += 'd' * num_dims

    wkb_string += struct.pack(byte_fmt, *coords)
    return wkb_string


def __dump_linestring(obj, big_endian, type_byte_str, num_dims):
    raise NotImplementedError


__dumps_registry = {
    'Point': __dump_point,
    'LineString': __dump_linestring,
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
    elif type_bytes in (WKB_Z['Point'], WKB_M['Point']):
        coords = struct.unpack('%sddd' % endian_token, data_bytes)
    elif type_bytes == WKB_ZM['Point']:
        coords = struct.unpack('%sddd' % endian_token, data_bytes)

    return dict(type='Point', coordinates=list(coords))


def __load_linestring(big_endian, type_bytes, data_bytes):
    raise NotImplementedError


__loads_registry = {
    'Point': __load_point,
    'LineString': __load_linestring,
}
