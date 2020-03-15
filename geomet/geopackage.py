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

import binascii
import struct

from geomet.util import as_bin_str, take
from geomet.wkb import (
    _get_geom_type,
    _unsupported_geom_type,
    _dumps_registry,
    _loads_registry,
    BIG_ENDIAN,
    LITTLE_ENDIAN,
)


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

    endianness = as_bin_str(take(1, string))
    if endianness == BIG_ENDIAN:
        big_endian = True
    elif endianness == LITTLE_ENDIAN:
        big_endian = False
    else:
        raise ValueError("Invalid endian byte: '0x%s'. Expected 0x00 or 0x01"
                         % binascii.hexlify(endianness.encode()).decode())

    endian_token = '>' if big_endian else '<'

    header_bytes = as_bin_str(take(_GeoPackageConstants.GEOPACKAGE_HEADER_LEN, string))
    _check_is_valid(header_bytes)

    type_bytes = as_bin_str(take(4, string))
    if not big_endian:
        # To identify the type, order the type bytes in big endian:
        type_bytes = type_bytes[::-1]

    geom_type, type_bytes, has_srid = _get_geom_type(type_bytes)
    srid = None
    if has_srid:
        srid_field = as_bin_str(take(4, string))
        [srid] = struct.unpack('%si' % endian_token, srid_field)

    data_bytes = string

    importer = _loads_registry.get(geom_type)

    if importer is None:
        _unsupported_geom_type(geom_type)

    data_bytes = iter(data_bytes)
    result = importer(big_endian, type_bytes, data_bytes)
    if has_srid:
        # As mentioned in the docstring above, include both approaches to
        # indicating the SRID.
        result['meta'] = {'srid': int(srid)}
        result['crs'] = {
            'type': 'name',
            'properties': {'name': 'EPSG%s' % srid},
        }
    return result


class _GeoPackageConstants:
    GEOPACKAGE_MAGIC1 = 0x47
    GEOPACKAGE_MAGIC2 = 0x50
    GEOPACKAGE_VERSION1 = 0x00
    GEOPACKAGE_FLAGS_LITTLEENDIAN_NOENVELOPE = 0x01
    GEOPACKAGE_HEADER_LEN = 8
    GEOPACKAGE_NO_ENVELOPE_LEN = 0
    GEOPACKAGE_2D_ENVELOPE_LEN = 32
    GEOPACKAGE_3D_ENVELOPE_LEN = 48
    GEOPACKAGE_4D_ENVELOPE_LEN = 64


# class _GeoPackageFlags:
#     def __init__(self,):
#         pass
#
#
# class _GeoPackageHeader:
#     def __init__(self, ):
#         pass


def _unpack_header(header):
    g, p, version, flags, srid = struct.unpack("<BBBBI", header)
    empty = (flags >> 1) & 0x04
    envelope_indicator = (flags >> 1) & 0x07
    return



def _get_flags(data):
    return struct.unpack("<B", data[3])[0]


def _get_envelope_indicator_code(data):
    envelope_indicator = (_get_flags(data) >> 1) & 0x07
    return envelope_indicator


def is_valid(data):
    geopackage_header = struct.unpack("<BBBB", data[:4])
    if (geopackage_header[0] != _GeoPackageConstants.GEOPACKAGE_MAGIC1) \
            or (geopackage_header[1] != _GeoPackageConstants.GEOPACKAGE_MAGIC2):
        return False
    if geopackage_header[2] != _GeoPackageConstants.GEOPACKAGE_VERSION1:
        return False
    envelope_indicator = _get_envelope_indicator_code(data)
    if (envelope_indicator < 0) or (envelope_indicator > 4):
        return False
    return True


def _check_is_valid(data):
    if not is_valid(data):
        raise ValueError("Could not create geometry because of errors "
                           "while reading geopackage input.")


def _get_wkb_offset(data):
    envelope_indicator = _get_envelope_indicator_code(data)
    if envelope_indicator == 0:
        return _GeoPackageConstants.GEOPACKAGE_HEADER_LEN
    elif envelope_indicator == 1:
        return _GeoPackageConstants.GEOPACKAGE_HEADER_LEN + _GeoPackageConstants.GEOPACKAGE_2D_ENVELOPE_LEN
    elif envelope_indicator in (2, 3):
        return _GeoPackageConstants.GEOPACKAGE_HEADER_LEN + _GeoPackageConstants.GEOPACKAGE_3D_ENVELOPE_LEN
    elif envelope_indicator == 4:
        return _GeoPackageConstants.GEOPACKAGE_HEADER_LEN + _GeoPackageConstants.GEOPACKAGE_4D_ENVELOPE_LEN
    else:
        # this should be prevented by the check is isValidGeoPackage, just defensive coding
        raise ValueError("Could not create geometry because of errors "
                           "while reading geopackage input.")


def _geopackage_header_is_little_endian(data):
    return _get_flags(data) & 0x01


def _get_srid(data):
    if _geopackage_header_is_little_endian(data):
        (srid,) = struct.unpack("<I", data[4:8])
    else:
        (srid,) = struct.unpack(">I", data[4:8])
    return srid


def _generate_geopackage_header(obj):
    return struct.pack("<BBBBI", _GeoPackageConstants.GEOPACKAGE_MAGIC1,
                       _GeoPackageConstants.GEOPACKAGE_MAGIC2,
                       _GeoPackageConstants.GEOPACKAGE_VERSION1,
                       _GeoPackageConstants.GEOPACKAGE_FLAGS_LITTLEENDIAN_NOENVELOPE,
                       obj.get('meta', {}).get('srid', 0))
