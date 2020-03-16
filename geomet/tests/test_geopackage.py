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

import unittest

from geomet import geopackage


class TestGeoPackageLoads(unittest.TestCase):
    def test_loads_2d_noenvelope_with_srid(self):
        gpkg = (  # GPKG header
            b'GP'  # "magic"
            b'\x00'  # version
            b'\x01'  # flags
            b'\xe6\x10\x00\x00'  # SRID
            b'\x01\x01\x00\x00\x00\xf0\x9e\xa0\xa7\x05;#@hZ\xbd\x93\x83GC@'  # WKB geom
        )
        expected = {'type': 'Point', 'coordinates': [9.615277517659223, 38.55870291467437], 'meta': {'srid': 4326}, 'crs': {'type': 'name', 'properties': {'name': 'EPSG4326'}}}

        self.assertEqual(expected, geopackage.loads(gpkg))

    def test_loads_2d_envelope_with_srid(self):
        gpkg = (
            b'GP'
            b'\x00'
            b'\x02'
            b'\xe6\x10\x00\x00' 
            b'\xf0\x9e\xa0\xa7\x05;#@hZ\xbd\x93\x83GC@\xf0\x9e\xa0\xa7\x05;#@hZ\xbd\x93\x83GC@'  # Envelope
            b'\x01\x01\x00\x00\x00\xf0\x9e\xa0\xa7\x05;#@hZ\xbd\x93\x83GC@'  # WKB
        )
        expected = {'type': 'Point', 'coordinates': [9.615277517659223, 38.55870291467437], 'meta': {'srid': 4326, 'envelope': (9.615277517659223, 38.55870291467437, 9.615277517659223, 38.55870291467437)}, 'crs': {'type': 'name', 'properties': {'name': 'EPSG4326'}}}

        self.assertEqual(expected, geopackage.loads(gpkg))
