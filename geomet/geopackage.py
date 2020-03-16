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

from geomet.util import as_bin_str, take
from geomet import wkb


def dump(obj, destination_file, decimals=16, envelope=True):
    pass


def load(source_file):
    pass


def dumps(obj, decimals=16, envelope=True):
    pass


def loads(string):
    """
    Envelope is added in the 'bbox' member of the geojson as per the GeoJSON spec, per [1].

    References:
        [1] https://tools.ietf.org/html/rfc7946#section-5
    """
    string = iter(string)

    header = as_bin_str(take(_GeoPackageConstants.HEADER_LEN, string))

    _check_is_valid(header)
    g, p, version, empty, envelope_indicator, is_little_endian, srid = _unpack_header(header)

    wkb_offset = _get_wkb_offset(envelope_indicator)
    envelope_data = as_bin_str(take((wkb_offset - _GeoPackageConstants.HEADER_LEN), string))

    if envelope_data:
        envelope = _get_envelope(envelope_indicator, envelope_data, is_little_endian)

    result = wkb.loads(string)

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
    FLAGS_LITTLEENDIAN_NOENVELOPE = 0x01
    FLAGS_LITTLEENDIAN_2DENVELOPE = 0x03
    HEADER_LEN = 8
    ENVELOPE_2D_LEN = 32
    ENVELOPE_3D_LEN = 48
    ENVELOPE_4D_LEN = 64
    ENVELOPE_MASK = 0b00001111
    EMPTY_GEOM_MASK = 0b00011111
    ENDIANESS_MASK = 0b00000001


_geopackage_envelope_formatters = {
    0: '',
    1: 'dddd',
    2: 'dddddd',
    3: 'dddddd',
    4: 'dddddddd',
}


def _unpack_header(header):
    g, p, version, flags, srid = struct.unpack("<BBBBI", header)
    empty, envelope_indicator, endianess = _parse_flags(flags)
    return g, p, version, empty, envelope_indicator, endianess, srid


def _parse_flags(flags):
    endianess = flags & _GeoPackageConstants.ENDIANESS_MASK
    envelope_indicator = (flags & _GeoPackageConstants.ENVELOPE_MASK) >> 1
    empty = (flags & _GeoPackageConstants.EMPTY_GEOM_MASK) >> 4
    return empty, envelope_indicator, endianess


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
                           "while reading geopackage input.")


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


def _get_envelope(envelope_indicator, envelope, header_is_little_endian):
    fmt = _geopackage_envelope_formatters[envelope_indicator]
    if header_is_little_endian:
        fmt = '<' + fmt
    else:
        fmt = '>' + fmt
    return struct.unpack(fmt, envelope)


def _build_flags(empty, envelope_indicator, endianess=1):
    flags = 0b0
    if empty:
        flags = (flags | 1) << 3
    if envelope_indicator:
        flags = (flags | envelope_indicator) << 1

    flags = flags | endianess
    return flags


def _generate_geopackage_header(obj):
    # empty = 0 if len(obj['coordinates'])
    bbox_coords = len(obj.get('bbox', []))

    header = struct.pack("<BBBBI", _GeoPackageConstants.MAGIC1,
                       _GeoPackageConstants.MAGIC2,
                       _GeoPackageConstants.VERSION1,
                       _build_flags(0, 0, 1),  # Defaults to little endian!
                       obj.get('meta', {}).get('srid', 0))
