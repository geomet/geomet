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
    def test_loads_noenvelope_with_srid(self):
        gpkg = b'GP\x00\x01\x11\x0f\x00\x00\x01\x01\x00\x00\x00\x16\xfb\xcb&\xe5\xd1W\xc1\x80?5.\xb4\xdb:\xc1'
        expected = {'type': 'Point', 'coordinates': [-6244244.6062, -1760180.1805000007], 'meta': {'srid': 3857}, 'crs': {'type': 'name', 'properties': {'name': 'EPSG3857'}}}

        self.assertEqual(expected, geopackage.loads(gpkg))

