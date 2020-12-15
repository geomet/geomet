#  Copyright 2020 Tom Caruso & individual contributors
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import struct as _struct

from geomet.util import (
    as_bin_str as _as_bin_str,
    take as _take,
    endian_token as _endian_token
)
from geomet import wkb as _wkb


def dump(obj, dest_file, big_endian=True):
    """
    Dump GeoJSON-like `dict` to GeoPackage binary
    and write it to the `dest_file`.

    :param dict obj:
        A GeoJSON-like dictionary. It must at least the keys 'type' and
        'coordinates'.
    :param dest_file:
        Open and writable file-like object.
    :param bool big_endian:
        specify endianess of the dumped object.

    :return:
    """
    dest_file.write(dumps(obj, big_endian))


def load(source_file):
    """
    Load a GeoJSON `dict` object from a ``source_file`` containing
    GeoPackage (as a byte string).

    :param source_file:
        Open and readable file-like object.

    :return:
        A GeoJSON `dict` representing the geometry read from the file.
    """
    return loads(source_file.read())


def dumps(obj, big_endian=True):
    """
    Dump a GeoJSON-like dict to a GeoPackage bytestring.


    If the dict contains a top-level 'meta' key like so:

    ```
    'meta': {'srid': 4326}
    ```
    then the srid will be added to the geopackage header, but *not*
    to the WKB geometry header.


    If the dict contains a top-level 'bbox' key like so:

    ```
    'bbox': [0, 0, 3, 3]
    ```

    Then an envelope will be added to the geopackage header
    with this information.


    If the geometry's coordinates are empty (an empty list)
    then the geopackage header's "empty" flag will be set,
    denoting that this geometry has no coordinates.

    Please note that while this library can parse geopackages
    with a mixed byte-order in the header, it will only produce
    blobs with consistent byte order (albeit properly marked as such).
    That means you cannot product a geopackage with e.g. little-endian
    header and big-endian WKB geometry.

    :param dict obj:
        The geojson geometry to dump
    :param bool big_endian:
        if True, the geopackage binary will use big-endian
        byte order, little-endian otherwise.

    :return bytes:
        bytestring representing the geometry in geopackage
        format.
    """
    header = _build_geopackage_header(obj, not big_endian)
    result = _wkb._dumps(obj, big_endian, include_meta=False)
    return header + result


def loads(string):
    """
    Construct a GeoJSON `dict` from geopackage (string).

    This function strips the geopackage header from the
    string and passes the remaining WKB geometry to the
    `geomet.wkb.loads` function.

    The envelope, if present, is added to the GeoJSON as
    a key called 'bbox' as per the GeoJSON spec, [1].

    If an SRID is specified in the geopackage header
    AND the wkb header, the SRID in the geopackage header
    will take precedence and will replace that SRID
    in the returned dict.

    [1] https://tools.ietf.org/html/rfc7946#section-5

    :param bytes string:
        geopackage byte string.
    :return dict:
        GeoJSON represented the parsed geopackage binary.
    """
    string = iter(string)

    header = _as_bin_str(_take(_GeoPackage.HEADER_LEN, string))

    _check_is_valid(header)
    g, p, version, empty, envelope_indicator, is_little_endian, srid = (
        _parse_header(header)
    )

    wkb_offset = _get_wkb_offset(envelope_indicator)
    left_to_take = (wkb_offset - _GeoPackage.HEADER_LEN)
    envelope_data = _as_bin_str(_take(left_to_take, string))

    if envelope_data:
        envelope = _parse_envelope(
            envelope_indicator, envelope_data, is_little_endian
        )

    result = _wkb.loads(string)

    if srid:
        result['meta'] = {'srid': int(srid)}
        result['crs'] = {
            'type': 'name',
            'properties': {'name': 'EPSG%s' % srid},
        }

    if envelope_data:
        result['bbox'] = envelope

    return result


class _GeoPackage:
    """
    Much more information on geopackage structure
    can be found here: http://www.geopackage.org/spec/#gpb_format
    """
    # The ascii letter 'G'
    MAGIC1 = 0x47
    # The ascii letter 'P'
    MAGIC2 = 0x50
    VERSION1 = 0x00
    HEADER_LEN = 8
    HEADER_PACK_FMT = "BBBBI"
    ENVELOPE_2D_LEN = 32
    ENVELOPE_3D_LEN = 48
    ENVELOPE_4D_LEN = 64
    ENVELOPE_MASK = 0b00001111
    EMPTY_GEOM_MASK = 0b00011111
    ENDIANNESS_MASK = 0b00000001


# map the "envelope indicator" integer we get out of the geopackage header
# to the dimensionality of the envelope.
# more info here: http://www.geopackage.org/spec/#gpb_format
# in the "flags" section, bits 3, 2, 1.
_indicator_to_dim = {
    0: 0,
    1: 4,
    2: 6,
    3: 6,
    4: 8,
}

# Map the dimensionality of our envelope to the indicator
# integer we will use in the geopackage binary header.
# because we have no way to tell between Z and M values,
# if the geometry has 3 dimensions we default to assume Z.
_dim_to_indicator = {
    0: 0,
    4: 1,
    6: 2,
    8: 4
}


def is_valid(data):
    """
    Check if the data represents a valid geopackage
    geometry. Input can be either the full geometry or
    just the header.

    :param bytes data:
        bytes representing the geopackage binary.

    :return (bool, str):
        Is the geopackage valid, if not, string describing why
    """
    g, p, version, _, envelope_indicator, _, _ = _parse_header(data[:8])
    if (g != _GeoPackage.MAGIC1) or (p != _GeoPackage.MAGIC2):
        return False, "Missing Geopackage header magic bytes"
    if version != _GeoPackage.VERSION1:
        return False, "Geopackage version must be 0"
    if (envelope_indicator < 0) or (envelope_indicator > 4):
        return False, "Envelope indicator must be between 0-4"
    return True, ""


def _header_is_little_endian(header):
    """
    Check to see if the header is encoded
    as little endian or big endian.

    Either the entire binary blob or
    just the header can be passed in.

    :param bytes header:
        geopackage header or binary blob

    :return bool: is the header little endian
    """
    (flags,) = _struct.unpack("B", header[3:4])
    return flags & _GeoPackage.ENDIANNESS_MASK


def _parse_header(header):
    """
    Unpack all information from the geopackage
    header, including "magic" GP bytes. Returns
    all of them so we can confirm that this
    geopackage is validly formed. Can also accept
    the full binary blob.

    :param header:
        the header or the full geometry.

    :return 7-tuple:
        all attributes stored in the binary header.
    """
    is_little_endian = _header_is_little_endian(header)
    fmt = _endian_token(is_little_endian) + _GeoPackage.HEADER_PACK_FMT

    g, p, version, flags, srid = _struct.unpack(
        fmt, header[:_GeoPackage.HEADER_LEN]
    )
    empty, envelope_indicator, endianness = _parse_flags(flags)
    return g, p, version, empty, envelope_indicator, endianness, srid


def _parse_flags(flags):
    """
    Parse the bits in the "flags" byte
    of the geopackage header to retrieve
    useful information. We specifically parse
    the endianness, the envelope indicator,
    and the "empty" flag.

    Much more info can be found in
    the documentation [1].

    [1] http://www.geopackage.org/spec/#gpb_format
    :param byte flags:
        The "flags" byte of a geopackage header.

    :return tuple:
    """
    endianness = flags & _GeoPackage.ENDIANNESS_MASK
    envelope_indicator = (flags & _GeoPackage.ENVELOPE_MASK) >> 1
    empty = (flags & _GeoPackage.EMPTY_GEOM_MASK) >> 4
    return empty, envelope_indicator, endianness


def _build_flags(empty, envelope_indicator, is_little_endian=1):
    """
    Create the "flags" byte which goes into
    the geopackage header. Much more info
    can be found in the documentation [1].

    [1] http://www.geopackage.org/spec/#gpb_format

    :param int empty:
        0 or 1 indicating whether the geometry is empty.
        True and False also work as expected.
    :param int envelope_indicator:
        indicates the dimensionality of the envelope.
    :param int is_little_endian:
        0 or 1 (or False / True) indicating
        whether the header should be
        little-endian encoded.

    :return byte:
        geopackage header flags
    """
    flags = 0b0
    if empty:
        flags = (flags | 1) << 3
    if envelope_indicator:
        flags = flags | envelope_indicator

    return (flags << 1) | is_little_endian


def _build_geopackage_header(obj, is_little_endian):
    """
    Create the geopackage header for the input object.
    Looks for a 'bbox' key on the geometry to use
    for an envelope, and a 'meta' key with an
    SRID to encode into the header.

    :param dict obj:
        a geojson object
    :param bool is_little_endian:
        which endianness to use when
        encoding the data.

    :return bytes: geopackage header.
    """
    # Collect geometry metadata.
    empty = 1 if len(obj['coordinates']) == 0 else 0
    envelope = obj.get('bbox', [])
    srid = obj.get('meta', {}).get('srid', 0)

    try:
        envelope_indicator = _dim_to_indicator[len(envelope)]
    except KeyError:
        raise ValueError("Bounding box must be of length 2*n where "
                         "n is the number of dimensions represented "
                         "in the contained geometries.")

    pack_args = [
        _GeoPackage.MAGIC1,
        _GeoPackage.MAGIC2,
        _GeoPackage.VERSION1,
        # This looks funny, but _build_flags wants a 1 or 0 for
        # "little endian" because it uses it to `or` with the bits.
        # Conveniently, in Python, False == 0 and True == 1, so
        # we can pass the boolean right in and it works as expected.
        _build_flags(empty, envelope_indicator, is_little_endian),
        srid
    ]

    pack_fmt = _endian_token(is_little_endian) + _GeoPackage.HEADER_PACK_FMT

    # This has no effect if we have a 0 envelope indicator.
    pack_fmt += ('d' * _indicator_to_dim[envelope_indicator])
    pack_args.extend(envelope)

    return _struct.pack(pack_fmt, *pack_args)


def _check_is_valid(data):
    """
    Raise if the header is not valid geopackage.

    :param bytes data: Geopackage data or header.

    :return None:
    """
    valid, reason = is_valid(data)
    if not valid:
        raise ValueError("Could not read Geopackage geometry "
                         "because of errors: " + reason)


def _get_wkb_offset(envelope_indicator):
    """
    Get the full byte offset at which the WKB geometry lies
    in the geopackage geometry.

    :param int envelope_indicator:
        indicates the dimensionality of the envelope.

    :return int:
        number of bytes until the beginning of the
        WKB geometry.

    """
    base_len = _GeoPackage.HEADER_LEN
    return (base_len * _indicator_to_dim[envelope_indicator]) + base_len


def _parse_envelope(envelope_indicator, envelope, is_little_endian):
    """
    Parse a geopackage envelope bytestring into an n-tuple
    of floats.

    :param int envelope_indicator:
        indicates the dimensionality of the envelope.
    :param bytes envelope:
        Bytestring of the envelope values.
    :param bool is_little_endian:
        how to pack the bytes in the envelope.

    :return tuple[float]: Geometry envelope.
    """
    pack_fmt = _endian_token(is_little_endian)
    pack_fmt += ('d' * _indicator_to_dim[envelope_indicator])
    return _struct.unpack(pack_fmt, envelope)
