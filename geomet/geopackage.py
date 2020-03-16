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

    """
    string = iter(string)

    header = as_bin_str(take(_GeoPackageConstants.HEADER_LEN, string))
    _check_is_valid(header)
    g, p, version, flags, srid, envelope_indicator = _unpack_header(header)

    wkb_offset = _get_wkb_offset(envelope_indicator)
    envelope_data = as_bin_str(take((wkb_offset - _GeoPackageConstants.HEADER_LEN), string))

    print("envelope indicator:", envelope_indicator)
    print(envelope_data)
    if envelope_data:
        print(envelope_data)
        envelope = _get_envelope(envelope_indicator, envelope_data)
        print(envelope)

    result = wkb.loads(string)

    if srid:
        result['meta'] = {'srid': int(srid)}
        result['crs'] = {
            'type': 'name',
            'properties': {'name': 'EPSG%s' % srid},
        }

    if envelope_data:
        result['meta']['envelope'] = envelope

    return result


class _GeoPackageConstants:
    MAGIC1 = 0x47
    MAGIC2 = 0x50
    VERSION1 = 0x00
    FLAGS_LITTLEENDIAN_NOENVELOPE = 0x01
    HEADER_LEN = 8
    ENVELOPE_2D_LEN = 32
    ENVELOPE_3D_LEN = 48
    ENVELOPE_4D_LEN = 64


_geopackage_envelope_formatters = {
    0: '',
    1: 'dddd',
    2: 'dddddd',
    3: 'dddddd',
    4: 'dddddddd',
}


def _unpack_header(header):
    g, p, version, flags, srid = struct.unpack("<BBBBI", header)
    envelope_indicator = (flags >> 1) & 0x07
    return g, p, version, flags, srid, envelope_indicator


def is_valid(data):
    g, p, version, flags, srid, envelope_indicator = _unpack_header(data[:8])
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


def _geopackage_header_is_little_endian(flags):
        return flags & 0x01


def _get_wkb_offset(envelope_indicator):
    if envelope_indicator == 0:
        return _GeoPackageConstants.HEADER_LEN
    elif envelope_indicator == 1:
        return _GeoPackageConstants.HEADER_LEN + _GeoPackageConstants.ENVELOPE_2D_LEN
    elif envelope_indicator in (2, 3):
        return _GeoPackageConstants.HEADER_LEN + _GeoPackageConstants.ENVELOPE_3D_LEN
    elif envelope_indicator == 4:
        return _GeoPackageConstants.HEADER_LEN + _GeoPackageConstants.ENVELOPE_4D_LEN


def _get_envelope(envelope_indicator, envelope):
    return struct.unpack(_geopackage_envelope_formatters[envelope_indicator], envelope)


def _generate_geopackage_header(obj):
    return struct.pack("<BBBBI", _GeoPackageConstants.MAGIC1,
                       _GeoPackageConstants.MAGIC2,
                       _GeoPackageConstants.VERSION1,
                       _GeoPackageConstants.FLAGS_LITTLEENDIAN_NOENVELOPE,
                       obj.get('meta', {}).get('srid', 0))
