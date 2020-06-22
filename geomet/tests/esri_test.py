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

import os
import six
import sys
sys.path.insert(0, r"C:\SVN\geomet_ajc_master")
import json
import tempfile
import unittest
from geomet import esri

IS_PY3 = six.PY3
IS_PY34 = six.PY34

esri_json_pt = {"x":25282,"y":43770,"spatialReference":{"wkid":3857}}
esri_json_mpt = {
            "points" : [ [-97.06138,32.837], [-97.06133,32.836], [-97.06124,32.834], [-97.06127,32.832] ],
            "spatialReference" : {"wkid" : 4326}
}
esri_json_polylines = {
                "paths" : [ [ [-97.06138,32.837], [-97.06133,32.836], [-97.06124,32.834], [-97.06127,32.832] ], 
                            [ [-97.06326,32.759], [-97.06298,32.755] ]],
                "spatialReference" : {"wkid" : 4326}
}
esri_json_polygon = {
            "rings" : [ [ [-97.06138,32.837], [-97.06133,32.836], [-97.06124,32.834], [-97.06127,32.832], [-97.06138,32.837] ], 
                        [ [-97.06326,32.759], [-97.06298,32.755], [-97.06153,32.749], [-97.06326,32.759] ]],
            "spatialReference" : {"wkid" : 4326}
}

gj_pt = {'type': 'Point', 'coordinates': (25282, 43770)}
gj_multi_linestring = {'type': 'MultiLineString', 'coordinates': [[(-97.06138, 32.837), (-97.06133, 32.836), (-97.06124, 32.834), (-97.06127, 32.832)], [(-97.06326, 32.759), (-97.06298, 32.755)]]} 
gj_lintstring =   { "type": "LineString","coordinates": [ [100.0, 100.0], [5.0, 5.0] ]}
gj_multi_polygon = {'type': 'MultiPolygon', 'coordinates': [[[(-97.06138, 32.837), (-97.06133, 32.836), (-97.06124, 32.834), (-97.06127, 32.832), (-97.06138, 32.837)]], [[(-97.06326, 32.759), (-97.06298, 32.755), (-97.06153, 32.749), (-97.06326, 32.759)]]]}
gj_polygon = { "type": "Polygon","coordinates": [[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ]]}
gj_multi_pt = {'type': 'Multipoint', 'coordinates': [[-97.06138, 32.837], [-97.06133, 32.836], [-97.06124, 32.834], [-97.06127, 32.832]]}

class TestIOReaderWriter(unittest.TestCase):
    """Tests the load/dump methods"""
    def test_io_dump(self):
        """
        Tests the `dump` method
        """
        vcheck = {"x": 25282, "y": 43770, "spatialReference": {"wkid": 4326}}
        if IS_PY3:            
            with tempfile.TemporaryDirectory() as d:
                fp = os.path.join(d, "test.json")
                assert esri.dump(gj_pt, fp)
                with open(fp, 'r') as r:
                    self.assertTrue(json.loads(r.read()) == vcheck)
                self.assertTrue(os.path.isfile(fp))
        else:
            d = tempfile.gettempdir()
            fp = os.path.join(d, "test.json")
            assert esri.dump(gj_pt, fp)
            with open(fp, 'r') as r:
                self.assertTrue(json.loads(r.read()) == vcheck)
            self.assertTrue(os.path.isfile(fp))
            os.remove(fp)
    def test_io_load(self):
        """
        Tests the `load` method
        """
        vcheck = {'type': 'Point', 'coordinates': (25282, 43770)}
        if IS_PY3:            
            with tempfile.TemporaryDirectory() as d:
                fp = os.path.join(d, "test.json")
                
                self.assertEqual(esri.load(esri.dump(gj_pt, fp)),vcheck)
        else:
            d = tempfile.gettempdir()
            fp = os.path.join(d, "test.json")
            self.assertEqual(esri.load(esri.dump(gj_pt, fp)),vcheck)            
            if os.path.isfile(fp):
                os.remove(fp)

class TestEsriJSONtoGeoJSON(unittest.TestCase):
    """
    Tests converting Esri to Geo JSON
    """
    def test_loads_unsupported_geom_type(self):
        """Tests loading invalid geometry type """
        if six.PY34:            
            invalid = {'Tetrahedron' : [[1,2,34], [2,3,4], [4,5,6]], 'spatialReference' : {'wkid' : 4326}}
            with self.assertRaises(ValueError) as ar:
                esri.loads(invalid)
            self.assertTrue(str(ar.exception).lower().find('invalid esrijson') > -1)
        else:
            invalid = {'Tetrahedron' : [[1,2,34], [2,3,4], [4,5,6]], 'spatialReference' : {'wkid' : 4326}}
            with self.assertRaises(ValueError) as ar:
                esri.loads(invalid)
            self.assertEqual("Invalid EsriJSON: {'Tetrahedron': [[1, 2, 34], [2, 3, 4], [4, 5, 6]], 'spatialReference': {'wkid': 4326}}",
                             str(ar.exception))            
    def test_loads_to_geojson_point(self):
        """Tests Loading Esri Point Geometry to Point GeoJSON"""
        self.assertEqual(esri.loads(esri_json_pt),
                          {'type': 'Point', 'coordinates': (25282, 43770)})
    def test_loads_to_geojson_multipoint(self):
        """Tests Loading Esri MultiPoint Geometry to MultiPoint GeoJSON"""
        self.assertEqual(esri.loads(esri_json_mpt),
                          {'type': 'Multipoint', 'coordinates': [[-97.06138, 32.837], [-97.06133, 32.836], 
                          [-97.06124, 32.834], [-97.06127, 32.832]]})
    def test_loads_to_geojson_linstring(self):
        """Tests Loading Esri Point Geometry to MultiLineString GeoJSON"""
        self.assertEqual(esri.loads(esri_json_polylines),
                          {'type': 'MultiLineString', 'coordinates': [[(-97.06138, 32.837), (-97.06133, 32.836), (-97.06124, 32.834), (-97.06127, 32.832)], 
                          [(-97.06326, 32.759), (-97.06298, 32.755)]]})
    def test_loads_to_geojson_polygon(self):
        """Tests Loading Esri Polygon Geometry to MultiPolygon GeoJSON"""
        self.assertEqual(esri.loads(esri_json_polygon),
                         {'type': 'MultiPolygon', 'coordinates': [
                             [[(-97.06138, 32.837), (-97.06133, 32.836), (-97.06124, 32.834), (-97.06127, 32.832), (-97.06138, 32.837)]], 
                         [[(-97.06326, 32.759), (-97.06298, 32.755), (-97.06153, 32.749), (-97.06326, 32.759)]]
                         ]})
    def test_loads_empty_pt_to_gj(self):
        """Tests Loading an empty Esri JSON Point to GeoJSON"""
        geom = {"x":None,"y":None,"spatialReference":{"wkid":3857}}
        self.assertEqual(esri.loads(geom),
                          {'type': 'Point', 'coordinates': ()})
    def test_loads_to_empty_mpt_to_gj(self):
        """Tests Loading an empty Esri JSON MultiPoint to GeoJSON"""
        geom = {
            "points" : [],
            "spatialReference" : {"wkid" : 4326}
        }
        geom_match = {'type': 'Multipoint', 'coordinates': []}
        self.assertEqual(esri.loads(geom),
                          geom_match)
    def test_loads_empty_polyline_to_gj(self):
        """Tests Loading an empty Esri JSON Polyline to GeoJSON"""
        geom = {
                "paths" : [],
                "spatialReference" : {"wkid" : 4326}
        }
        geom_match = {'type': 'MultiLineString', 'coordinates': []}
        self.assertEqual(esri.loads(geom),
                          geom_match)
    def test_loads_empty_polygon_to_gj(self):
        """Tests Loading an empty Esri JSON Polygon to GeoJSON"""
        geom = {
            "rings" : [],
            "spatialReference" : {"wkid" : 4326}
        }
        geom_match = {'type': 'MultiPolygon', 'coordinates': []}
        self.assertEqual(esri.loads(geom),
                          geom_match)

class TestGeoJSONtoEsriJSON(unittest.TestCase):
    """
    Tests the `dumps/dump` functions which will convert GeoJSON to
    Esri JSON
    """
    def test_dumps_to_esrijson_point(self):
        """Tests Converting GeoJSON Point to Esri JSON"""
        self.assertEqual(esri.dumps(gj_pt),
                          {'spatialReference': {'wkid': 4326}, 'x': 25282, 'y': 43770})
    def test_dumps_to_esrijson_multipoint(self):
        """Tests Converting GeoJSON MultiPoint to Esri JSON MultiPoint"""
        self.assertEqual(esri.dumps(gj_multi_pt),
                          esri_json_mpt)
    def test_dumps_to_esrijson_polyline1(self):
        """Tests Converting GeoJSON LineString to Esri JSON Polyline"""
        self.assertEqual(esri.dumps(gj_lintstring),
                          {'paths': [[[100.0, 100.0], [5.0, 5.0]]], 'spatialReference': {'wkid': 4326}})
    def test_dumps_to_esrijson_polyline2(self):
        """Tests Converting GeoJSON MultiLineString to Esri JSON Polyline"""
        
        vcheck = {'paths': [[(-97.06138, 32.837), (-97.06133, 32.836), (-97.06124, 32.834), (-97.06127, 32.832)], 
        [(-97.06326, 32.759), (-97.06298, 32.755)]], 'spatialReference': {'wkid': 4326}}
        self.assertEqual(esri.dumps(gj_multi_linestring),
                          vcheck)
    def test_dumps_to_esrijson_polygon1(self):
        """Tests Converting GeoJSON Polygon to Esri JSON Polygon"""
        vcheck = {'rings': [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]], 'spatialReference': {'wkid': 4326}}
        self.assertEqual(esri.dumps(gj_polygon),
                          vcheck)
    def test_dumps_to_esrijson_polygon2(self):
        """Tests Converting GeoJSON MultiPolygon to Esri JSON Polygon"""
        vcheck = {'rings': [[(-97.06138, 32.837), (-97.06133, 32.836), (-97.06124, 32.834), (-97.06127, 32.832), (-97.06138, 32.837)], 
        [(-97.06326, 32.759), (-97.06298, 32.755), (-97.06153, 32.749), (-97.06326, 32.759)]], 'spatialReference': {'wkid': 4326}}
        self.assertEqual(esri.dumps(gj_multi_polygon),
                          vcheck)

if __name__ == "__main__":
    unittest.main()
    


