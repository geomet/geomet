import struct

#: '\x00': The first byte of any WKB string. Indicates big endian byte
#: ordering for the data.
BIG_ENDIAN = '\x00'
#: '\x01': The first byte of any WKB string. Indicates little endian byte
#: ordering for the data.
LITTLE_ENDIAN = '\x01'

#: Mapping of GeoJSON geometry types to the "2D" 4-byte binary string
#: representation for WKB. "2D" indicates that the geometry is 2-dimensional,
#: X and Y components.
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
WKB_M = {
    'Point': '\x00\x00\x20\x01',
    'LineString': '\x00\x00\x20\x02',
    'Polygon': '\x00\x00\x00\x03',
    'MultiPoint': '\x00\x00\x20\x04',
    'MultiLineString': '\x00\x00\x20\x05',
    'MultiPolygon': '\x00\x00\x20\x06',
    'GeometryCollection': '\x00\x00\x20\x07',
}

#: Mapping of GeoJSON geometry types to the "ZM" 4-byte binary string
#: representation for WKB. "ZM" indicates that the geometry is 4-dimensional,
#: with X, Y, Z, and M ("Measure") components.
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


def dump(obj, dest_file):
    pass


def load(source_file):
    pass


def dumps(obj, big_endian=False):
    """
    Dump a GeoJSON-like `dict` to a WKB string.
    """
    pass


def loads(string):
    """
    Construct a GeoJson `dict` from WKB (`string`).
    """
    pass
