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

import struct

from geomet.util import as_bin_str as _as_bin_str, take as _take
from geomet import wkb as _wkb


def dump(obj, dest_file, big_endian=True):
    dest_file.write(dumps(obj, big_endian))


def load(source_file):
    loads(source_file.read())


def dumps(obj, big_endian=True):
    header = _build_geopackage_header(obj, not big_endian)
    result = _wkb._dumps(obj, big_endian, include_meta=False)
    return header + result


def loads(string):
    """
    Envelope is added in the 'bbox' member of the geojson
    as per the GeoJSON spec, per [1].

    References:
        [1] https://tools.ietf.org/html/rfc7946#section-5
    """
    string = iter(string)

    header = _as_bin_str(_take(_GeoPackageConstants.HEADER_LEN, string))

    _check_is_valid(header)
    g, p, version, empty, envelope_indicator, is_little_endian, srid = _unpack_header(header)

    wkb_offset = _get_wkb_offset(envelope_indicator)
    left_to_take = (wkb_offset - _GeoPackageConstants.HEADER_LEN)
    envelope_data = _as_bin_str(_take(left_to_take, string))

    if envelope_data:
        envelope = _parse_envelope(envelope_indicator,
                                   envelope_data,
                                   is_little_endian)

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


class _GeoPackageConstants:
    MAGIC1 = 0x47
    MAGIC2 = 0x50
    VERSION1 = 0x00
    HEADER_LEN = 8
    ENVELOPE_2D_LEN = 32
    ENVELOPE_3D_LEN = 48
    ENVELOPE_4D_LEN = 64
    ENVELOPE_MASK = 0b00001111
    EMPTY_GEOM_MASK = 0b00011111
    ENDIANNESS_MASK = 0b00000001


_geopackage_envelope_formatters = {
    0: '',
    1: 'dddd',
    2: 'dddddd',
    3: 'dddddd',
    4: 'dddddddd',
}


def _header_is_little_endian(header):
    (flags,) = struct.unpack("B", header[3:4])
    return flags & _GeoPackageConstants.ENDIANNESS_MASK


def _unpack_header(header):
    if _header_is_little_endian(header):
        fmt = "<BBBBI"
    else:
        fmt = ">BBBBI"
    g, p, version, flags, srid = struct.unpack(fmt, header)
    empty, envelope_indicator, endianness = _parse_flags(flags)
    return g, p, version, empty, envelope_indicator, endianness, srid


def _parse_flags(flags):
    endianness = flags & _GeoPackageConstants.ENDIANNESS_MASK
    envelope_indicator = (flags & _GeoPackageConstants.ENVELOPE_MASK) >> 1
    empty = (flags & _GeoPackageConstants.EMPTY_GEOM_MASK) >> 4
    return empty, envelope_indicator, endianness


def _build_flags(empty, envelope_indicator, endianness=1):
    flags = 0b0
    if empty:
        flags = (flags | 1) << 3
    if envelope_indicator:
        flags = flags | envelope_indicator

    return (flags << 1) | endianness


def _build_geopackage_header(obj, is_little_endian):

    empty = 1 if len(obj['coordinates']) == 0 else 0
    bbox_coords = obj.get('bbox', [])
    num_bbox_coords = len(bbox_coords)

    srid = obj.get('meta', {}).get('srid', 0)

    if num_bbox_coords == 0:
        envelope_indicator = 0
    elif num_bbox_coords == 4:
        envelope_indicator = 1
    elif num_bbox_coords == 6:
        # Can we find out if this geometry has Z or M? Let's assume Z.
        envelope_indicator = 2
    elif num_bbox_coords == 8:
        envelope_indicator = 4
    else:
        raise ValueError("Bounding box must be of length 2*n where "
                         "n is the number of dimensions represented "
                         "in the contained geometries.")

    fmt = "BBBBI"

    if is_little_endian:
        fmt = '<' + fmt
    else:
        fmt = '>' + fmt

    pack_args = [
        _GeoPackageConstants.MAGIC1,
        _GeoPackageConstants.MAGIC2,
        _GeoPackageConstants.VERSION1,
        _build_flags(empty, envelope_indicator, is_little_endian),
        srid
    ]

    if envelope_indicator:
        fmt += _geopackage_envelope_formatters[envelope_indicator]
        pack_args.extend(bbox_coords)

    return struct.pack(fmt, *pack_args)


def is_valid(data):
    g, p, version, _, envelope_indicator, _, _ = _unpack_header(data[:8])
    if (g != _GeoPackageConstants.MAGIC1) \
            or (p != _GeoPackageConstants.MAGIC2):
        return False
    if version != _GeoPackageConstants.VERSION1:
        return False
    if (envelope_indicator < 0) or (envelope_indicator > 4):
        return False
    return True


def _check_is_valid(data):
    if not is_valid(data):
        raise ValueError("Could not create geometry because of errors "
                         "while reading geopackage header.")


def _get_wkb_offset(envelope_indicator):
    base_len = _GeoPackageConstants.HEADER_LEN
    if envelope_indicator == 0:
        return base_len
    elif envelope_indicator == 1:
        return base_len + base_len * 4
    elif envelope_indicator in (2, 3):
        return base_len + base_len * 6
    elif envelope_indicator == 4:
        return base_len + base_len * 8


def _parse_envelope(envelope_indicator, envelope, is_little_endian):
    fmt = _geopackage_envelope_formatters[envelope_indicator]
    if is_little_endian:
        fmt = '<' + fmt
    else:
        fmt = '>' + fmt
    return struct.unpack(fmt, envelope)


def _build_envelope(envelope_indicator, envelope, is_little_endian):

    fmt = _geopackage_envelope_formatters[envelope_indicator]
    if is_little_endian:
        fmt = '<' + fmt
    else:
        fmt = '>' + fmt
    return struct.pack(fmt, *envelope)
