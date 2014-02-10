import binascii
import six
import struct

from geomet.util import block_splitter
from itertools import chain

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

__INT_TO_DIM_LABEL = {2: '2D', 3: 'Z', 4: 'ZM'}


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


def __header_bytefmt_byteorder(geom_type, num_dims, big_endian):
    """
    Utility function to get the WKB header (endian byte + type header), byte
    format string, and byte order string.
    """
    dim = __INT_TO_DIM_LABEL.get(num_dims)
    if dim is None:
        pass  # TODO: raise

    type_byte_str = __WKB[dim][geom_type]

    if big_endian:
        header = BIG_ENDIAN
        byte_fmt = b'>'
        byte_order = '>'
    else:
        header = LITTLE_ENDIAN
        byte_fmt = b'<'
        byte_order = '<'
        # reverse the byte ordering for little endian
        type_byte_str = type_byte_str[::-1]

    header += type_byte_str
    byte_fmt += b'd' * num_dims

    return header, byte_fmt, byte_order


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
    coords = obj['coordinates']
    num_dims = len(coords)

    wkb_string, byte_fmt, _ = __header_bytefmt_byteorder(
        'Point', num_dims, big_endian
    )

    wkb_string += struct.pack(byte_fmt, *coords)
    return wkb_string


def __dump_linestring(obj, big_endian):
    """
    Dump a GeoJSON-like `dict` to a linestring WKB string.

    Input parameters and output are similar to :func:`__dump_point`.
    """
    coords = obj['coordinates']
    vertex = coords[0]
    # Infer the number of dimensions from the first vertex
    num_dims = len(vertex)

    wkb_string, byte_fmt, byte_order = __header_bytefmt_byteorder(
        'LineString', num_dims, big_endian
    )
    # append number of vertices in linestring
    wkb_string += struct.pack('%sl' % byte_order, len(coords))

    for vertex in coords:
        wkb_string += struct.pack(byte_fmt, *vertex)

    return wkb_string


def __dump_polygon(obj, big_endian):
    """
    Dump a GeoJSON-like `dict` to a polygon WKB string.

    Input parameters and output are similar to :funct:`__dump_point`.
    """
    coords = obj['coordinates']
    vertex = coords[0][0]
    # Infer the number of dimensions from the first vertex
    num_dims = len(vertex)

    wkb_string, byte_fmt, byte_order = __header_bytefmt_byteorder(
        'Polygon', num_dims, big_endian
    )

    # number of rings:
    wkb_string += struct.pack('%sl' % byte_order, len(coords))
    for ring in coords:
        # number of verts in this ring:
        wkb_string += struct.pack('%sl' % byte_order, len(ring))
        for vertex in ring:
            wkb_string += struct.pack(byte_fmt, *vertex)

    return wkb_string


def __dump_multipoint(obj, big_endian):
    """
    Dump a GeoJSON-like `dict` to a multipoint WKB string.

    Input parameters and output are similar to :funct:`__dump_point`.
    """
    coords = obj['coordinates']
    vertex = coords[0]
    num_dims = len(vertex)

    wkb_string, byte_fmt, byte_order = __header_bytefmt_byteorder(
        'MultiPoint', num_dims, big_endian
    )

    point_type = __WKB[__INT_TO_DIM_LABEL.get(num_dims)]['Point']
    if big_endian:
        point_type = BIG_ENDIAN + point_type
    else:
        point_type = LITTLE_ENDIAN + point_type[::-1]

    wkb_string += struct.pack('%sl' % byte_order, len(coords))
    for vertex in coords:
        # POINT type strings
        wkb_string += point_type
        wkb_string += struct.pack(byte_fmt, *vertex)

    return wkb_string


def __dump_multilinestring(obj, big_endian):
    """
    Dump a GeoJSON-like `dict` to a multilinestring WKB string.

    Input parameters and output are similar to :funct:`__dump_point`.
    """
    coords = obj['coordinates']
    vertex = coords[0][0]
    num_dims = len(vertex)

    wkb_string, byte_fmt, byte_order = __header_bytefmt_byteorder(
        'MultiLineString', num_dims, big_endian
    )

    ls_type = __WKB[__INT_TO_DIM_LABEL.get(num_dims)]['LineString']
    if big_endian:
        ls_type = BIG_ENDIAN + ls_type
    else:
        ls_type = LITTLE_ENDIAN + ls_type[::-1]

    # append the number of linestrings
    wkb_string += struct.pack('%sl' % byte_order, len(coords))

    for linestring in coords:
        wkb_string += ls_type
        # append the number of vertices in each linestring
        wkb_string += struct.pack('%sl' % byte_order, len(linestring))
        for vertex in linestring:
            wkb_string += struct.pack(byte_fmt, *vertex)

    return wkb_string


def __dump_multipolygon(obj, big_endian):
    """
    Dump a GeoJSON-like `dict` to a multipolygon WKB string.

    Input parameters and output are similar to :funct:`__dump_point`.
    """
    coords = obj['coordinates']
    vertex = coords[0][0][0]
    num_dims = len(vertex)

    wkb_string, byte_fmt, byte_order = __header_bytefmt_byteorder(
        'MultiPolygon', num_dims, big_endian
    )

    poly_type = __WKB[__INT_TO_DIM_LABEL.get(num_dims)]['Polygon']
    if big_endian:
        poly_type = BIG_ENDIAN + poly_type
    else:
        poly_type = LITTLE_ENDIAN + poly_type[::-1]

    # apped the number of polygons
    wkb_string += struct.pack('%sl' % byte_order, len(coords))

    for polygon in coords:
        # append polygon header
        wkb_string += poly_type
        # append the number of rings in this polygon
        wkb_string += struct.pack('%sl' % byte_order, len(polygon))
        for ring in polygon:
            # append the number of vertices in this ring
            wkb_string += struct.pack('%sl' % byte_order, len(ring))
            for vertex in ring:
                wkb_string += struct.pack(byte_fmt, *vertex)

    return wkb_string


def __dump_geometrycollection(obj, big_endian):
    # TODO: handle empty collections
    geoms = obj['geometries']
    # determine the dimensionality (2d, 3d, 4d) of the collection
    # by sampling the first geometry
    first_geom = geoms[0]
    rest = geoms[1:]

    first_wkb = dumps(first_geom, big_endian=big_endian)
    first_type = first_wkb[1:5]
    if not big_endian:
        first_type = first_type[::-1]

    if first_type in WKB_2D.values():
        num_dims = 2
    elif first_type in WKB_Z.values():
        num_dims = 3
    elif first_type in WKB_ZM.values():
        num_dims = 4

    wkb_string, byte_fmt, byte_order = __header_bytefmt_byteorder(
        'GeometryCollection', num_dims, big_endian
    )
    # append the number of geometries
    wkb_string += struct.pack('%sl' % byte_order, len(geoms))

    wkb_string += first_wkb
    for geom in rest:
        wkb_string += dumps(geom, big_endian=big_endian)

    return wkb_string


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


def __load_polygon(big_endian, type_bytes, data_bytes):
    endian_token = '>' if big_endian else '<'

    is_m = False

    if type_bytes in WKB_2D.values():
        num_dims = 2
    elif type_bytes in WKB_Z.values():
        num_dims = 3
    elif type_bytes in WKB_M.values():
        num_dims = 3
        is_m = True
    elif type_bytes in WKB_ZM.values():
        num_dims = 4

    coords = []
    [num_rings] = struct.unpack('%sl' % endian_token, data_bytes[:4])

    data_bytes = data_bytes[4:]
    while len(data_bytes) > 0:
        ring = []
        [num_verts] = struct.unpack('%sl' % endian_token, data_bytes[:4])
        data_bytes = data_bytes[4:]

        verts_wkb = data_bytes[:8 * num_verts * num_dims]
        verts = block_splitter(verts_wkb, 8)
        if six.PY2:
            verts = (b''.join(x) for x in verts)
        elif six.PY3:
            verts = (b''.join(bytes([y]) for y in x) for x in verts)
        for vert_wkb in block_splitter(verts, num_dims):
            values = [struct.unpack('%sd' % endian_token, x)[0]
                      for x in vert_wkb]
            if is_m:
                values.insert(2, 0.0)
            ring.append(values)
        coords.append(ring)
        data_bytes = data_bytes[8 * num_verts * num_dims:]

    return dict(type='Polygon', coordinates=coords)


def __load_multipoint(big_endian, type_bytes, data_bytes):
    endian_token = '>' if big_endian else '<'

    is_m = False

    if type_bytes in WKB_2D.values():
        num_dims = 2
    elif type_bytes in WKB_Z.values():
        num_dims = 3
    elif type_bytes in WKB_M.values():
        num_dims = 3
        is_m = True
    elif type_bytes in WKB_ZM.values():
        num_dims = 4

    if is_m:
        dim = 'M'
    else:
        dim = __INT_TO_DIM_LABEL[num_dims]

    coords = []
    [num_points] = struct.unpack('%sl' % endian_token, data_bytes[:4])

    data_bytes = data_bytes[4:]
    while len(data_bytes) > 0:
        point_endian = data_bytes[0]
        point_type = data_bytes[1:5]
        if six.PY3:
            point_endian = bytes([point_endian])
        values = struct.unpack('%s%s' % (endian_token, 'd' * num_dims),
                               data_bytes[5:5 + 8 * num_dims])
        values = list(values)
        if is_m:
            values.insert(2, 0.0)

        if big_endian:
            assert point_endian == BIG_ENDIAN
            assert point_type == __WKB[dim]['Point']
        else:
            assert point_endian == LITTLE_ENDIAN
            assert point_type[::-1] == __WKB[dim]['Point']

        coords.append(list(values))

        data_bytes = data_bytes[5 + 8 * num_dims:]

    return dict(type='MultiPoint', coordinates=coords)


__dumps_registry = {
    'Point':  __dump_point,
    'LineString': __dump_linestring,
    'Polygon': __dump_polygon,
    'MultiPoint': __dump_multipoint,
    'MultiLineString': __dump_multilinestring,
    'MultiPolygon': __dump_multipolygon,
    'GeometryCollection': __dump_geometrycollection,
}


__loads_registry = {
    'Point': __load_point,
    'LineString': __load_linestring,
    'Polygon': __load_polygon,
    'MultiPoint': __load_multipoint,
    #'MultiLineString': __load_multilinestring,
    #'MultiPolygon': __load_multipolygon,
    #'GeometryCollection': __load_geometrycollection,
}
