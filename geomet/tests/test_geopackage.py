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
import unittest

from geomet import geopackage


def build_header(magic1=0x47, magic2=0x50, version=0x00, flags=0x01, srid=4326):
    return struct.pack("<BBBBI", magic1, magic2, version, flags, srid)


def build_flags(empty=0, envelope_indicator=0, endianess=1):
    return geopackage._build_flags(empty, envelope_indicator, endianess)


class TestGeoPackageLoads(unittest.TestCase):
    def test_loads_noenvelope_with_srid(self):
        gpkg = (  # GPKG header
            b'GP'  # "magic"
            b'\x00'  # version
            b'\x01'  # flags
            b'\xe6\x10\x00\x00'  # SRID
            b'\x01\x01\x00\x00\x00\xf0\x9e\xa0\xa7\x05;#@hZ\xbd\x93\x83GC@'  # WKB geom
        )
        expected = {'type': 'Point', 'coordinates': [9.615277517659223, 38.55870291467437], 'meta': {'srid': 4326},
                    'crs': {'type': 'name', 'properties': {'name': 'EPSG4326'}}}

        self.assertEqual(expected, geopackage.loads(gpkg))

    def test_loads_2d_envelope_with_srid(self):
        gpkg = (
            b'GP'
            b'\x00'
            b'\x03'
            b'\xe6\x10\x00\x00'
            b'\xf0\x9e\xa0\xa7\x05;#@hZ\xbd\x93\x83GC@\xf0\x9e\xa0\xa7\x05;#@hZ\xbd\x93\x83GC@'  # Envelope
            b'\x01\x01\x00\x00\x00\xf0\x9e\xa0\xa7\x05;#@hZ\xbd\x93\x83GC@'  # WKB
        )
        expected = {'type': 'Point',
                    'bbox': (9.615277517659223, 38.55870291467437, 9.615277517659223, 38.55870291467437),
                    'coordinates': [9.615277517659223, 38.55870291467437], 'meta': {'srid': 4326},
                    'crs': {'type': 'name', 'properties': {'name': 'EPSG4326'}}}

        self.assertEqual(expected, geopackage.loads(gpkg))


class TestRoundTrip(unittest.TestCase):
    def test_without_envelope_with_srid_little_endian(self):
        gpkg = (  # GPKG header
            b'GP'  # "magic"
            b'\x00'  # version
            b'\x01'  # flags
            b'\xe6\x10\x00\x00'  # SRID
            b'\x01\x01\x00\x00\x00\xf0\x9e\xa0\xa7\x05;#@hZ\xbd\x93\x83GC@'  # WKB geom
        )
        expected = {
            'type': 'Point',
            'coordinates': [9.615277517659223, 38.55870291467437],
            'meta': {'srid': 4326},
            'crs': {'type': 'name', 'properties': {'name': 'EPSG4326'}}
        }

        result = geopackage.loads(gpkg)
        self.assertEqual(expected, result)
        self.assertEqual(gpkg, geopackage.dumps(result, big_endian=False))

    def test_with_envelope_and_srid_big_endian(self):
        expected_loads = {
            'coordinates': [1.0, 1.0],
            'type': 'Point',
            'meta': {'srid': 4326},
            'crs': {'type': 'name', 'properties': {'name': 'EPSG4326'}},
            'bbox': (1.0, 1.0, 1.0, 1.0)
        }

        expected_dumps = (b'GP\x00\x02\x00\x00\x10\xe6?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00'
                          b'\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00'
                          b'\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00'
                          b'\x00')

        dumps_result = geopackage.dumps(expected_loads)
        self.assertEqual(expected_dumps, dumps_result)

        loads_result = geopackage.loads(dumps_result)
        self.assertEqual(expected_loads, loads_result)



class TestBuildFlags(unittest.TestCase):

    def check_build_and_parse_flags(self, empty, envelope, endian, expected):
        flags = geopackage._build_flags(empty, envelope, endian)

        self.assertEqual(expected, flags)

        _empty, _envelope, _endian = geopackage._parse_flags(flags)
        self.assertEqual(empty, _empty)
        self.assertEqual(envelope, _envelope)
        self.assertEqual(endian, _endian)

    def test_empty_no_envelope_little_endian(self):
        empty, envelope, endian, expected = 1, 0, 1, 0b00010001
        self.check_build_and_parse_flags(empty, envelope, endian, expected)

    def test_empty_2d_envelope_little_endian(self):
        empty, envelope, endian, expected = 1, 1, 1, 0b00010011
        self.check_build_and_parse_flags(empty, envelope, endian, expected)

    def test_empty_3d_envelope_little_endian(self):
        empty, envelope, endian, expected = 1, 2, 1, 0b00010101
        self.check_build_and_parse_flags(empty, envelope, endian, expected)

    def test_empty_3m_envelope_little_endian(self):
        empty, envelope, endian, expected = 1, 3, 1, 0b00010111
        self.check_build_and_parse_flags(empty, envelope, endian, expected)

    def test_empty_4d_envelope_little_endian(self):
        empty, envelope, endian, expected = 1, 4, 1, 0b00011001
        self.check_build_and_parse_flags(empty, envelope, endian, expected)

    def test_not_empty_no_envelope_big_endian(self):
        empty, envelope, endian, expected = 0, 0, 0, 0b00000000
        self.check_build_and_parse_flags(empty, envelope, endian, expected)

    def test_not_empty_no_envelope_little_endian(self):
        empty, envelope, endian, expected = 0, 0, 1, 0b00000001
        self.check_build_and_parse_flags(empty, envelope, endian, expected)

    def test_not_empty_2d_envelope_big_endian(self):
        empty, envelope, endian, expected = 0, 1, 0, 0b00000010
        self.check_build_and_parse_flags(empty, envelope, endian, expected)

    def test_not_empty_2d_envelope_little_endian(self):
        empty, envelope, endian, expected = 0, 1, 1, 0b00000011
        self.check_build_and_parse_flags(empty, envelope, endian, expected)

    def test_not_empty_3dz_envelope_big_endian(self):
        empty, envelope, endian, expected = 0, 2, 0, 0b00000100
        self.check_build_and_parse_flags(empty, envelope, endian, expected)

    def test_not_empty_3dz_envelope_little_endian(self):
        empty, envelope, endian, expected = 0, 2, 1, 0b00000101
        self.check_build_and_parse_flags(empty, envelope, endian, expected)

    def test_not_empty_3dm_envelope_big_endian(self):
        empty, envelope, endian, expected = 0, 3, 0, 0b00000110
        self.check_build_and_parse_flags(empty, envelope, endian, expected)

    def test_not_empty_3dm_envelope_little_endian(self):
        empty, envelope, endian, expected = 0, 3, 1, 0b00000111
        self.check_build_and_parse_flags(empty, envelope, endian, expected)

    def test_not_empty_4d_envelope_big_endian(self):
        empty, envelope, endian, expected = 0, 4, 0, 0b00001000
        self.check_build_and_parse_flags(empty, envelope, endian, expected)

    def test_not_empty_4d_envelope_little_endian(self):
        empty, envelope, endian, expected = 0, 4, 1, 0b00001001
        self.check_build_and_parse_flags(empty, envelope, endian, expected)


class TestHeaderIsLittleEndian(unittest.TestCase):
    def test_little_endian(self):
        header = build_header(flags=0x01)
        self.assertTrue(geopackage._header_is_little_endian(header))

    def test_big_endian(self):
        header = build_header(flags=0x00)
        self.assertFalse(geopackage._header_is_little_endian(header))


class TestUnpackHeader(unittest.TestCase):
    pass

class TestIsValid(unittest.TestCase):

    def test_no_magic_g(self):
        header = build_header(magic1=0x00)
        self.assertFalse(geopackage.is_valid(header))

    def test_no_magic_p(self):
        header = build_header(magic2=0x00)
        self.assertFalse(geopackage.is_valid(header))

    def test_wrong_version(self):
        header = build_header(version=0x01)
        self.assertFalse(geopackage.is_valid(header))

    def test_out_of_bounds_envelope(self):
        flags = geopackage._build_flags(0, 5, 1)
        header = build_header(flags=flags)
        self.assertFalse(geopackage.is_valid(header))

    def test_check_is_valid_raises(self):
        header = build_header(magic1=0x58)
        with self.assertRaises(ValueError) as exc:
            geopackage._check_is_valid(header)

        self.assertRegex(str(exc.exception), "Could not create geometry because of errors "
                                             "while reading geopackage header.")

    def check_is_valid_not_raise(self):
        header = build_header()
        geopackage._check_is_valid(header)


class TestGetWKBOffset(unittest.TestCase):
    def test_no_envelope(self):
        indicator = 0
        expected = 8
        self.assertEqual(expected, geopackage._get_wkb_offset(indicator))

    def test_2d_envelope(self):
        indicator = 1
        expected = 40
        self.assertEqual(expected, geopackage._get_wkb_offset(indicator))

    def test_3dz_envelope(self):
        indicator = 2
        expected = 56
        self.assertEqual(expected, geopackage._get_wkb_offset(indicator))

    def test_3dm_envelope(self):
        indicator = 3
        expected = 56
        self.assertEqual(expected, geopackage._get_wkb_offset(indicator))

    def test_4d_envelope(self):
        indicator = 4
        expected = 72
        self.assertEqual(expected, geopackage._get_wkb_offset(indicator))


class TestBuildGeoPackageHeader(unittest.TestCase):
    def test_build_header_no_envelope_no_srid_little_endian(self):
        geom = {
            'coordinates': [1.0, 1.0],
            'type': 'Point'
        }
        header = geopackage._build_geopackage_header(geom, header_is_little_endian=True)

        expected = b'GP\x00\x01\x00\x00\x00\x00'

        self.assertEqual(expected, header)

    def test_build_header_no_envelope_no_srid_big_endian(self):
        geom = {
            'coordinates': [1.0, 1.0],
            'type': 'Point'
        }
        header = geopackage._build_geopackage_header(geom, header_is_little_endian=False)

        expected = b'GP\x00\x00\x00\x00\x00\x00'

        self.assertEqual(expected, header)

    def test_build_header_no_envelope_with_srid_little_endian(self):
        geom = {
            'coordinates': [1.0, 1.0],
            'type': 'Point',
            'meta': {'srid': 4326}
        }
        header = geopackage._build_geopackage_header(geom, header_is_little_endian=True)

        expected = b'GP\x00\x01\xe6\x10\x00\x00'

        self.assertEqual(expected, header)

    def test_build_header_no_envelope_with_srid_big_endian(self):
        geom = {
            'coordinates': [1.0, 1.0],
            'type': 'Point',
            'meta': {'srid': 4326}
        }
        header = geopackage._build_geopackage_header(geom, header_is_little_endian=False)

        expected = b'GP\x00\x00\x00\x00\x10\xe6'

        self.assertEqual(expected, header)

    def test_build_header_with_2d_envelope_with_srid_little_endian(self):
        geom = {
            'coordinates': [1.0, 1.0],
            'type': 'Point',
            'meta': {
                'srid': 4326
            },
            'bbox': (1.0, 1.0, 1.0, 1.0)
        }
        header = geopackage._build_geopackage_header(geom, header_is_little_endian=True)

        expected = (b'GP\x00\x03\xe6\x10\x00\x00'
                    b'\x00\x00\x00\x00\x00\x00\xf0?'
                    b'\x00\x00\x00\x00\x00\x00\xf0?'
                    b'\x00\x00\x00\x00\x00\x00\xf0?'
                    b'\x00\x00\x00\x00\x00\x00\xf0?')

        self.assertEqual(expected, header)

    def test_build_header_with_2d_envelope_with_srid_big_endian(self):
        geom = {
            'coordinates': [1.0, 1.0],
            'type': 'Point',
            'meta': {'srid': 4326},
            'bbox': (1.0, 1.0, 1.0, 1.0)
        }
        header = geopackage._build_geopackage_header(geom, header_is_little_endian=False)

        expected = (b'GP\x00\x02\x00\x00\x10\xe6'
                    b'?\xf0\x00\x00\x00\x00\x00\x00'
                    b'?\xf0\x00\x00\x00\x00\x00\x00'
                    b'?\xf0\x00\x00\x00\x00\x00\x00'
                    b'?\xf0\x00\x00\x00\x00\x00\x00')

        self.assertEqual(expected, header)

    def test_build_header_with_3d_envelope_with_srid_little_endian(self):
        geom = {
            'coordinates': [1.0, 1.0, 1.0],
            'type': 'Point',
            'meta': {'srid': 4326},
            'bbox': (1.0, 1.0, 1.0, 1.0, 1.0, 1.0)}
        header = geopackage._build_geopackage_header(geom, header_is_little_endian=True)

        expected = (b'GP\x00\x05\xe6\x10\x00\x00'
                    b'\x00\x00\x00\x00\x00\x00\xf0?'
                    b'\x00\x00\x00\x00\x00\x00\xf0?'
                    b'\x00\x00\x00\x00\x00\x00\xf0?'
                    b'\x00\x00\x00\x00\x00\x00\xf0?'
                    b'\x00\x00\x00\x00\x00\x00\xf0?'
                    b'\x00\x00\x00\x00\x00\x00\xf0?')

        self.assertEqual(expected, header)

    def test_build_header_with_3d_envelope_with_srid_big_endian(self):
        geom = {
            'coordinates': [1.0, 1.0, 1.0],
            'type': 'Point',
            'meta': {'srid': 4326},
            'bbox': (1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
        }
        header = geopackage._build_geopackage_header(geom, header_is_little_endian=False)

        expected = (b'GP\x00\x04\x00\x00\x10\xe6'
                    b'?\xf0\x00\x00\x00\x00\x00\x00'
                    b'?\xf0\x00\x00\x00\x00\x00\x00'
                    b'?\xf0\x00\x00\x00\x00\x00\x00'
                    b'?\xf0\x00\x00\x00\x00\x00\x00'
                    b'?\xf0\x00\x00\x00\x00\x00\x00'
                    b'?\xf0\x00\x00\x00\x00\x00\x00')

        self.assertEqual(expected, header)

    def test_build_header_with_4d_envelope_with_srid_little_endian(self):
        geom = {
            'coordinates': [1.0, 1.0, 1.0, 1.0],
            'type': 'Point',
            'meta': {'srid': 4326},
            'bbox': (1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
        }
        header = geopackage._build_geopackage_header(geom, header_is_little_endian=True)

        expected = (b'GP\x00\t\xe6\x10\x00\x00'
                    b'\x00\x00\x00\x00\x00\x00\xf0?'
                    b'\x00\x00\x00\x00\x00\x00\xf0?'
                    b'\x00\x00\x00\x00\x00\x00\xf0?'
                    b'\x00\x00\x00\x00\x00\x00\xf0?'
                    b'\x00\x00\x00\x00\x00\x00\xf0?'
                    b'\x00\x00\x00\x00\x00\x00\xf0?'
                    b'\x00\x00\x00\x00\x00\x00\xf0?'
                    b'\x00\x00\x00\x00\x00\x00\xf0?')

        self.assertEqual(expected, header)

    def test_build_header_with_4d_envelope_with_srid_big_endian(self):
        geom = {
            'coordinates': [1.0, 1.0, 1.0, 1.0],
            'type': 'Point',
            'meta': {'srid': 4326},
            'bbox': (1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
        }
        header = geopackage._build_geopackage_header(geom, header_is_little_endian=False)

        expected = (b'GP\x00\x08\x00\x00\x10\xe6'
                    b'?\xf0\x00\x00\x00\x00\x00\x00'
                    b'?\xf0\x00\x00\x00\x00\x00\x00'
                    b'?\xf0\x00\x00\x00\x00\x00\x00'
                    b'?\xf0\x00\x00\x00\x00\x00\x00'
                    b'?\xf0\x00\x00\x00\x00\x00\x00'
                    b'?\xf0\x00\x00\x00\x00\x00\x00'
                    b'?\xf0\x00\x00\x00\x00\x00\x00'
                    b'?\xf0\x00\x00\x00\x00\x00\x00')

        self.assertEqual(expected, header)

    def test_build_header_invalid_envelope(self):
        geom = {
            'coordinates': [1.0, 1.0],
            'type': 'Point',
            'meta': {'srid': 4326},
            'bbox': (1.0, 1.0, 1.0)
        }

        with self.assertRaises(ValueError) as exc:
            geopackage._build_geopackage_header(geom, header_is_little_endian=True)

            self.assertRegex(str(exc.exception), "Bounding box must be of length 2*n where "
                             "n is the number of dimensions represented "
                             "in the contained geometries.")
