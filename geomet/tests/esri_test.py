#  Copyright 2013 Lars Butler & individual contributors
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

from geomet.esri import _extract_geojson_srid
from geomet import InvalidGeoJSONException
from geomet import esri
import os
import json
import tempfile
import unittest

esri_json_pt = {"x": 25282, "y": 43770, "spatialReference": {"wkid": 3857}}
esri_json_mpt = {
    "points": [
        [-97.06138, 32.837], [-97.06133, 32.836],
        [-97.06124, 32.834], [-97.06127, 32.832],
    ],
    "spatialReference": {"wkid": 4326}
}
esri_json_mpt_srid_26955 = {
    "points": [
        [-97.06138, 32.837], [-97.06133, 32.836],
        [-97.06124, 32.834], [-97.06127, 32.832],
    ],
    "spatialReference": {"wkid": 26955}
}
esri_json_polylines = {
    "paths": [
        [[-97.06138, 32.837], [-97.06133, 32.836],
         [-97.06124, 32.834], [-97.06127, 32.832]],
        [[-97.06326, 32.759], [-97.06298, 32.755]]
    ],
    "spatialReference": {"wkid": 4326}
}
esri_json_polygon = {
    "rings": [
        [[-97.06138, 32.837], [-97.06133, 32.836], [-97.06124, 32.834],
         [-97.06127, 32.832], [-97.06138, 32.837]],
        [[-97.06326, 32.759], [-97.06298, 32.755],
         [-97.06153, 32.749], [-97.06326, 32.759]]
    ],
    "spatialReference": {"wkid": 4326}
}

gj_pt = {'type': 'Point', 'coordinates': (25282, 43770)}
gj_multi_linestring = {'type': 'MultiLineString',
                       'coordinates': [[(-97.06138,
                                         32.837),
                                        (-97.06133,
                                         32.836),
                                        (-97.06124,
                                         32.834),
                                        (-97.06127,
                                         32.832)],
                                       [(-97.06326,
                                         32.759),
                                        (-97.06298,
                                           32.755)]]}
gj_lintstring = {"type": "LineString",
                 "coordinates": [[100.0, 100.0], [5.0, 5.0]]}
gj_multi_polygon = {'type': 'MultiPolygon',
                    'coordinates': [[[(-97.06138,
                                       32.837),
                                      (-97.06133,
                                       32.836),
                                      (-97.06124,
                                       32.834),
                                      (-97.06127,
                                       32.832),
                                      (-97.06138,
                                       32.837)]],
                                    [[(-97.06326,
                                       32.759),
                                      (-97.06298,
                                        32.755),
                                        (-97.06153,
                                         32.749),
                                        (-97.06326,
                                         32.759)]]]}
gj_polygon = {"type": "Polygon", "coordinates": [
    [[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]]}
gj_multi_pt = {
    'type': 'MultiPoint',
    'coordinates': [
        [-97.06138, 32.837], [-97.06133, 32.836],
        [-97.06124, 32.834], [-97.06127, 32.832],
    ]
}


class TestIOReaderWriter(unittest.TestCase):
    """Tests the load/dump methods"""

    def test_io_dump(self):
        """
        Tests the `dump` method
        """
        vcheck = {"x": 25282, "y": 43770, "spatialReference": {"wkid": 4326}}
        with tempfile.TemporaryDirectory() as d:
            fp = os.path.join(d, "test.json")
            with open(fp, "w") as write_file:
                esri.dump(gj_pt, write_file)
            with open(fp, 'r') as r:
                data = r.read()
                data = json.loads(data)
                self.assertTrue(data == vcheck)
            self.assertTrue(os.path.isfile(fp))

    def test_io_load(self):
        """
        Tests the `load` method
        """
        with tempfile.TemporaryDirectory() as d:
            fp = os.path.join(d, "test.json")
            with open(fp, 'w') as w:
                esri.dump(gj_pt, w)
            with open(fp, 'r') as r:
                self.assertEqual(
                    esri.load(r),
                    {
                        'spatialReference': {'wkid': 4326},
                        'x': 25282,
                        'y': 43770,
                    }
                )


class TestEsriJSONtoGeoJSON(unittest.TestCase):
    """
    Tests converting Esri to Geo JSON
    """

    def test_loads_unsupported_geom_type(self):
        """Tests loading invalid geometry type """
        invalid = {'Tetrahedron': [[1, 2, 34], [2, 3, 4], [
            4, 5, 6]], 'spatialReference': {'wkid': 4326}}
        with self.assertRaises(InvalidGeoJSONException) as ar:
            esri.loads(json.dumps(invalid, sort_keys=True))
        self.assertEqual(
            'Invalid EsriJSON: '
            '{"Tetrahedron": [[1, 2, 34], [2, 3, 4], [4, 5, 6]], '
            '"spatialReference": {"wkid": 4326}}',
            str(ar.exception)
        )

    def test_loads_to_geojson_point(self):
        """Tests Loading Esri Point Geometry to Point GeoJSON"""
        self.assertEqual(esri.loads(json.dumps(esri_json_pt)),
                         {'type': 'Point', 'coordinates': (25282, 43770)})

    def test_loads_to_geojson_multipoint(self):
        """Tests Loading Esri MultiPoint Geometry to MultiPoint GeoJSON"""
        self.assertEqual(
            esri.loads(json.dumps(esri_json_mpt)),
            {
                'type': 'MultiPoint',
                'coordinates': [
                    [-97.06138, 32.837], [-97.06133, 32.836],
                    [-97.06124, 32.834], [-97.06127, 32.832],
                ],
            }
        )

    def test_loads_to_geojson_linstring(self):
        """Tests Loading Esri Point Geometry to MultiLineString GeoJSON"""
        self.assertEqual(esri.loads(json.dumps(esri_json_polylines)),
                         {'type': 'MultiLineString',
                          'coordinates': [[(-97.06138,
                                            32.837),
                                           (-97.06133,
                                            32.836),
                                           (-97.06124,
                                            32.834),
                                           (-97.06127,
                                            32.832)],
                                          [(-97.06326,
                                            32.759),
                                           (-97.06298,
                                              32.755)]]})

    def test_loads_to_geojson_polygon(self):
        """Tests Loading Esri Polygon Geometry to MultiPolygon GeoJSON"""
        self.assertEqual(
            esri.loads(json.dumps(esri_json_polygon)),
            {
                'type': 'MultiPolygon',
                'coordinates': [
                    [[(-97.06138, 32.837), (-97.06133, 32.836),
                      (-97.06124, 32.834), (-97.06127, 32.832),
                      (-97.06138, 32.837)]],
                    [[(-97.06326, 32.759), (-97.06298, 32.755),
                      (-97.06153, 32.749), (-97.06326, 32.759)]],
                ]
            }
        )

    def test_loads_empty_pt_to_gj(self):
        """Tests Loading an empty Esri JSON Point to GeoJSON"""
        geom = json.dumps(
            {"x": None, "y": None, "spatialReference": {"wkid": 3857}}
        )
        self.assertEqual(esri.loads(geom),
                         {'type': 'Point', 'coordinates': ()})

    def test_loads_to_empty_mpt_to_gj(self):
        """Tests Loading an empty Esri JSON MultiPoint to GeoJSON"""
        geom = json.dumps({
            "points": [],
            "spatialReference": {"wkid": 4326}
        })
        geom_match = {'type': 'MultiPoint', 'coordinates': []}
        self.assertEqual(esri.loads(geom),
                         geom_match)

    def test_loads_empty_polyline_to_gj(self):
        """Tests Loading an empty Esri JSON Polyline to GeoJSON"""
        geom = json.dumps({
            "paths": [],
            "spatialReference": {"wkid": 4326}
        })
        geom_match = {'type': 'MultiLineString', 'coordinates': []}
        self.assertEqual(esri.loads(geom), geom_match)

    def test_loads_empty_polygon_to_gj(self):
        """Tests Loading an empty Esri JSON Polygon to GeoJSON"""
        geom = json.dumps({
            "rings": [],
            "spatialReference": {"wkid": 4326}
        })
        geom_match = {'type': 'MultiPolygon', 'coordinates': []}
        self.assertEqual(esri.loads(geom), geom_match)


class TestGeoJSONtoEsriJSON(unittest.TestCase):
    """
    Tests the `dumps/dump` functions which will convert GeoJSON to
    Esri JSON
    """

    def test_dumps_to_esrijson_point(self):
        """Tests Converting GeoJSON Point to Esri JSON"""
        self.assertEqual(
            esri.dumps(gj_pt), {
                'spatialReference': {
                    'wkid': 4326}, 'x': 25282, 'y': 43770})

    def test_dumps_to_esrijson_multipoint(self):
        """Tests Converting GeoJSON MultiPoint to Esri JSON MultiPoint"""
        self.assertEqual(esri.dumps(gj_multi_pt),
                         esri_json_mpt)

    def test_dumps_to_esrijson_polyline1(self):
        """Tests Converting GeoJSON LineString to Esri JSON Polyline"""
        self.assertEqual(
            esri.dumps(gj_lintstring),
            {
                'paths': [[[100.0, 100.0], [5.0, 5.0]]],
                'spatialReference': {'wkid': 4326},
            }
        )

    def test_dumps_to_esrijson_polyline2(self):
        """Tests Converting GeoJSON MultiLineString to Esri JSON Polyline"""

        vcheck = {'paths': [[(-97.06138,
                              32.837),
                             (-97.06133,
                              32.836),
                             (-97.06124,
                              32.834),
                             (-97.06127,
                              32.832)],
                            [(-97.06326,
                              32.759),
                             (-97.06298,
                                32.755)]],
                  'spatialReference': {'wkid': 4326}}
        self.assertEqual(esri.dumps(gj_multi_linestring),
                         vcheck)

    def test_dumps_to_esrijson_polygon1(self):
        """Tests Converting GeoJSON Polygon to Esri JSON Polygon"""
        vcheck = {'rings': [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [
            100.0, 1.0], [100.0, 0.0]]], 'spatialReference': {'wkid': 4326}}
        self.assertEqual(esri.dumps(gj_polygon),
                         vcheck)

    def test_dumps_to_esrijson_polygon2(self):
        """Tests Converting GeoJSON MultiPolygon to Esri JSON Polygon"""
        vcheck = {'rings': [[(-97.06138,
                              32.837),
                             (-97.06133,
                              32.836),
                             (-97.06124,
                              32.834),
                             (-97.06127,
                              32.832),
                             (-97.06138,
                              32.837)],
                            [(-97.06326,
                              32.759),
                             (-97.06298,
                                32.755),
                             (-97.06153,
                                32.749),
                             (-97.06326,
                                32.759)]],
                  'spatialReference': {'wkid': 4326}}
        self.assertEqual(esri.dumps(gj_multi_polygon),
                         vcheck)

    def test_srid_checks(self):
        """tests the srid functionality"""
        example = {
            "type": "Polygon",
            "coordinates":
            [
                [
                    [-91.23046875, 45.460130637921],
                    [-79.8046875, 49.837982453085],
                    [-69.08203125, 43.452918893555],
                    [-88.2421875, 32.694865977875],
                    [-91.23046875, 45.460130637921]
                ]
            ],
            "crs": {"type": "name", "properties": {"name": "EPSG:3857"}}
        }
        srid = _extract_geojson_srid(obj=example)
        self.assertTrue(srid == "3857")

    def test_multipolygon_nesting(self):
        expected = {
            'rings': [
                [[102, 2], [103, 2], [103, 3], [102, 3], [102, 2]],
                [[100, 0], [101, 0], [101, 1], [100, 1], [100, 0]],
                [
                    [100.2, 0.2], [100.2, 0.8], [100.8, 0.8],
                    [100.8, 0.2], [100.2, 0.2],
                ],
            ],
            'spatialReference': {'wkid': 4326},
        }
        geojson_mp = {
                "type": "MultiPolygon",
                "coordinates": [
                    [[[102, 2], [103, 2], [103, 3], [102, 3], [102, 2]]],
                    [
                        [[100, 0], [101, 0], [101, 1], [100, 1], [100, 0]],
                        [
                            [100.2, 0.2], [100.2, 0.8], [100.8, 0.8],
                            [100.8, 0.2], [100.2, 0.2],
                        ],
                    ],
                ],
            }
        actual = esri.dumps(geojson_mp)
        self.assertEqual(expected, actual)


class TestGeoJSONtoEsriJSONCustomSRID(unittest.TestCase):
    """Tests to convert GeoJSON to EsriJSON, with custom SRIDs.

    Proof for https://github.com/geomet/geomet/issues/99.
    """
    def test_dumps_to_esrijson_point_custom_srid(self):
        self.assertEqual(
            esri.dumps(gj_pt, srid=2062), {
                'spatialReference': {
                    'wkid': 2062}, 'x': 25282, 'y': 43770})

    def test_dumps_to_esrijson_multipoint_custom_srid(self):
        self.assertEqual(
            esri.dumps(gj_multi_pt, srid=26955),
            esri_json_mpt_srid_26955,
        )

    def test_dumps_to_esrijson_polyline_custom_srid(self):
        self.assertEqual(
            esri.dumps(gj_lintstring, srid=3572),
            {
                'paths': [[[100.0, 100.0], [5.0, 5.0]]],
                'spatialReference': {'wkid': 3572},
            }
        )

    def test_dumps_to_esrijson_polygon_custom_srid(self):
        vcheck = {'rings': [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [
            100.0, 1.0], [100.0, 0.0]]], 'spatialReference': {'wkid': 2263}}
        self.assertEqual(esri.dumps(gj_polygon, srid=2263),
                         vcheck)


if __name__ == "__main__":
    unittest.main()
