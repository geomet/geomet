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
try:
    import StringIO
except ImportError:
    import io
    StringIO = io

import geomet
import unittest

from geomet import wkt


WKT = {}
WKT['point'] = {
    '2d': 'POINT (0.0000000000000000 1.0000000000000000)',
    '3d': 'POINT (0.0000000000000000 -1.0000000000000000 2.0000000000000000)',
    '4d': ('POINT (-0.0000000000000000 -1.0000000000000000 '
           '-2.0000000000000000 -4.0000000000000000)'),
}
WKT['linestring'] = {
    '2d': ('LINESTRING (-100.0000000000000000 0.0000000000000000, '
           '-101.0000000000000000 -1.0000000000000000)'),
    '3d': ('LINESTRING ('
           '100.0000000000000000 0.0000000000000000 -60.0000000000000000, '
           '101.0000000000000000 1.0000000000000000 -65.2500000000000000)'),
    '4d': ('LINESTRING ('
           '100.0000000000000000 0.0000000000000000 -60.0000000000000000 '
           '0.1000000000000000, '
           '101.0000000000000000 1.0000000000000000 -65.2500000000000000 '
           '0.2000000000000000)'),
}
WKT['polygon'] = {
    '2d': ('POLYGON ((100.0010 0.0010, 101.1235 0.0010, 101.0010 1.0010, '
           '100.0010 0.0010), '
           '(100.2010 0.2010, 100.8010 0.2010, 100.8010 0.8010, '
           '100.2010 0.2010))'),
    '3d': ('POLYGON ((100.0 0.0 3.1, 101.0 0.0 2.1, 101.0 1.0 1.1, '
           '100.0 0.0 3.1), '
           '(100.2 0.2 3.1, 100.8 0.2 2.1, 100.8 0.8 1.1, 100.2 0.2 3.1))'),
    '4d': 'POLYGON ((1 2 3 4, 5 6 7 8, 9 10 11 12, 1 2 3 4))',
}
WKT['multipoint'] = {
    '2d': 'MULTIPOINT ((100.000 3.101), (101.000 2.100), (3.140 2.180))',
    '3d': ('MULTIPOINT ((100.00 3.10 1.00), (101.00 2.10 2.00), '
           '(3.14 2.18 3.00))'),
    '4d': ('MULTIPOINT ((100.00 3.10 1.00 0.00), (101.00 2.10 2.00 0.00), '
           '(3.14 2.18 3.00 0.00))'),

}
WKT['multilinestring'] = (
    'MULTILINESTRING ((0 -1, -2 -3, -4 -5), '
    '(1.66 -31023.5 1.1, 10000.9999 3.0 2.2, 100.9 1.1 3.3, 0 0 4.4))'
)
WKT['multipolygon'] = (
    'MULTIPOLYGON (((100.001 0.001, 101.001 0.001, 101.001 1.001, '
    '100.001 0.001), '
    '(100.201 0.201, 100.801 0.201, 100.801 0.801, '
    '100.201 0.201)), ((1 2 3 4, 5 6 7 8, 9 10 11 12, 1 2 3 4)))'
)


class WKTTestCase(unittest.TestCase):

    def test_dumps_unsupported_geom_type(self):
        geom = dict(type='Tetrahedron', coordinates=[])
        with self.assertRaises(ValueError) as ar:
            wkt.dumps(geom)
        self.assertEqual("Unsupported geometry type 'Tetrahedron'",
                         str(ar.exception))

    def test_loads_unsupported_geom_type(self):
        geom = 'TETRAHEDRON (0 0)'  # This obviously isn't a valid tetrahedron
        with self.assertRaises(ValueError) as ar:
            wkt.loads(geom)
        self.assertEqual("Unsupported geometry type 'TETRAHEDRON'",
                         str(ar.exception))

    def test_dumps_empty_geoms(self):
        types = [
            'Point',
            'LineString',
            'Polygon',
            'MultiPoint',
            'MultiLineString',
            'MultiPolygon',
        ]
        expected = ['%s EMPTY' % x.upper() for x in types]

        for i, t in enumerate(types):
            geom = dict(type=t, coordinates=[])
            self.assertEqual(expected[i], wkt.dumps(geom))

    def test_loads_empty_geoms(self):
        types = [
            'Point',
            'LineString',
            'Polygon',
            'MultiPoint',
            'MultiLineString',
            'MultiPolygon',
        ]
        wkts = ['%s EMPTY' % x.upper() for x in types]
        for i, each_wkt in enumerate(wkts):
            expected = dict(type=types[i], coordinates=[])
            self.assertEqual(expected, wkt.loads(each_wkt))

        self.assertEqual(dict(type='GeometryCollection', geometries=[]),
                         wkt.loads('GEOMETRYCOLLECTION EMPTY'))

    def test_dumps_empty_geometrycollection(self):
        geom = dict(type='GeometryCollection', geometries=[])
        self.assertEqual('GEOMETRYCOLLECTION EMPTY', wkt.dumps(geom))

    def test_malformed_geojson(self):
        bad_geojson = [
            # GEOMETRYCOLLECTIONs have 'geometries', not coordinates
            dict(type='GeometryCollection', coordinates=[]),
            # All other geometry types must have coordinates
            dict(type='Point'),
            # and a type
            dict(coordinates=[]),
        ]
        for each in bad_geojson:
            with self.assertRaises(geomet.InvalidGeoJSONException):
                wkt.dumps(each)


class TestFileInteractions(unittest.TestCase):
    def test_load(self):
        fobj = StringIO.StringIO()

        geom = 'POINT (0 0)'
        fobj.write(geom)
        fobj.seek(0)

        loaded = wkt.load(fobj)
        expected = dict(type='Point', coordinates=[0, 0])
        self.assertEqual(expected, loaded)

    def test_dump(self):
        fobj = StringIO.StringIO()

        geom = dict(type='Point', coordinates=[0, 0])
        wkt.dump(geom, fobj)
        fobj.seek(0)

        written = fobj.read()
        expected = 'POINT (0.0000000000000000 0.0000000000000000)'
        self.assertEqual(expected, written)


class PointDumpsTestCase(unittest.TestCase):

    def test_2d(self):
        # Tests a typical 2D Point case:
        pt = dict(type='Point', coordinates=[0.0, 1.0])
        expected = WKT['point']['2d']
        self.assertEqual(expected, wkt.dumps(pt))

    def test_3d(self):
        # Test for an XYZ/XYM Point:
        pt = dict(type='Point', coordinates=[0.0, -1.0, 2.0])
        expected = WKT['point']['3d']
        self.assertEqual(expected, wkt.dumps(pt))

    def test_4d(self):
        # Test for an XYZM Point:
        pt = dict(type='Point', coordinates=[-0.0, -1.0, -2.0, -4.0])
        expected = WKT['point']['4d']
        self.assertEqual(expected, wkt.dumps(pt))

    def test_2d_6_decimals(self):
        pt = dict(type='Point', coordinates=[-10, -77])
        expected = 'POINT (-10.000000 -77.000000)'
        self.assertEqual(expected, wkt.dumps(pt, decimals=6))

    def test_2d_srid4326(self):
        # SRID just from meta:
        pt = dict(type='Point', coordinates=[0.0, 1.0], meta=dict(srid=4326))
        expected = 'SRID=4326;' + WKT['point']['2d']
        self.assertEqual(expected, wkt.dumps(pt))

        # SRID from both meta and crs:
        pt = dict(
            type='Point', coordinates=[0.0, 1.0], meta=dict(srid=4326),
            crs={'type': 'name', 'properties': {'name': 'EPSG4326'}},
        )
        expected = 'SRID=4326;' + WKT['point']['2d']
        self.assertEqual(expected, wkt.dumps(pt))

        # SRID just from crs:
        pt = dict(
            type='Point', coordinates=[0.0, 1.0],
            crs={'type': 'name', 'properties': {'name': 'EPSG4326'}},
        )
        expected = 'SRID=4326;' + WKT['point']['2d']
        self.assertEqual(expected, wkt.dumps(pt))

        # Conflicting SRID from meta and crs:
        pt = dict(
            type='Point', coordinates=[0.0, 1.0], meta=dict(srid=4326),
            crs={'type': 'name', 'properties': {'name': 'EPSG4327'}},
        )
        expected = 'SRID=4326;' + WKT['point']['2d']
        with self.assertRaises(ValueError) as ar:
            wkt.dumps(pt)
        self.assertEqual('Ambiguous CRS/SRID values: 4326 and 4327',
                         str(ar.exception))


class PointLoadsTestCase(unittest.TestCase):

    def test_2d(self):
        pt = 'POINT (-0.0000000000000000 1.0000000000000000)'
        expected = dict(type='Point', coordinates=[0.0, 1.0])
        self.assertEqual(expected, wkt.loads(pt))

    def test_3d(self):
        pt = 'POINT (-0.0 -1.0 -2.0)'
        expected = dict(type='Point', coordinates=[0.0, -1.0, -2.0])
        self.assertEqual(expected, wkt.loads(pt))

    def test_4d(self):
        pt = 'POINT (0.0 1.0 2.0 -4.0)'
        expected = dict(type='Point', coordinates=[0.0, 1.0, 2.0, -4.0])
        self.assertEqual(expected, wkt.loads(pt))

    def test_raises_unmatched_paren(self):
        pt = 'POINT (0.0 1.0'
        with self.assertRaises(ValueError) as ar:
            wkt.loads(pt)
        self.assertEqual('Invalid WKT: `POINT (0.0 1.0`',
                         str(ar.exception))

    def test_raises_invalid_wkt(self):
        pt = 'POINT 0.0 1.0'
        with self.assertRaises(ValueError) as ar:
            wkt.loads(pt)
        self.assertEqual('Invalid WKT: `POINT 0.0 1.0`', str(ar.exception))

    def test_2d_srid664(self):
        pt = 'SRID=664;POINT (-0.0000000000000000 1.0000000000000000)'
        expected = dict(
            type='Point', coordinates=[0.0, 1.0], meta=dict(srid=664)
        )
        self.assertEqual(expected, wkt.loads(pt))


class LineStringDumpsTestCase(unittest.TestCase):

    def test_2d(self):
        # Test a typical 2D LineString case:
        ls = dict(type='LineString', coordinates=[[-100.0, 0.0],
                                                  [-101.0, -1.0]])
        expected = WKT['linestring']['2d']
        self.assertEqual(expected, wkt.dumps(ls))

    def test_3d(self):
        ls = dict(type='LineString', coordinates=[[100.0, 0.0, -60.0],
                                                  [101.0, 1.0, -65.25]])
        expected = WKT['linestring']['3d']
        self.assertEqual(expected, wkt.dumps(ls))

    def test_4d(self):
        ls = dict(type='LineString', coordinates=[[100.0, 0.0, -60.0, 0.1],
                                                  [101.0, 1.0, -65.25, 0.2]])
        expected = WKT['linestring']['4d']
        self.assertEqual(expected, wkt.dumps(ls))

    def test_2d_3_decimals(self):
        ls = dict(type='LineString', coordinates=[[100.0, 0.0], [101.0, 1.0]])
        expected = 'LINESTRING (100.000 0.000, 101.000 1.000)'
        self.assertEqual(expected, wkt.dumps(ls, decimals=3))

    def test_2d_srid4326(self):
        # Test a typical 2D LineString case:
        ls = dict(
            type='LineString',
            coordinates=[[-100.0, 0.0], [-101.0, -1.0]],
            meta=dict(srid=4326),
        )
        expected = 'SRID=4326;' + WKT['linestring']['2d']
        self.assertEqual(expected, wkt.dumps(ls))


class LineStringLoadsTestCase(unittest.TestCase):

    def test_2d(self):
        ls = 'LINESTRING (0 -1, -2 -3, -4 5)'
        expected = dict(type='LineString', coordinates=[[0.0, -1.0],
                                                        [-2.0, -3.0],
                                                        [-4.0, 5.0]])
        self.assertEqual(expected, wkt.loads(ls))

    def test_3d(self):
        ls = 'LINESTRING (0 1 2, 3 4 5)'
        expected = dict(type='LineString', coordinates=[[0.0, 1.0, 2.0],
                                                        [3.0, 4.0, 5.0]])
        self.assertEqual(expected, wkt.loads(ls))

    def test_4d(self):
        ls = 'LINESTRING (0 1 2 3, 4 5 6 7)'
        expected = dict(type='LineString', coordinates=[[0.0, 1.0, 2.0, 3.0],
                                                        [4.0, 5.0, 6.0, 7.0]])
        self.assertEqual(expected, wkt.loads(ls))

    def test_raises_unmatched_paren(self):
        ls = 'LINESTRING (0.0 1.0'
        with self.assertRaises(ValueError) as ar:
            wkt.loads(ls)
        self.assertEqual('Invalid WKT: `LINESTRING (0.0 1.0`',
                         str(ar.exception))

    def test_raises_invalid_wkt(self):
        ls = 'LINESTRING 0.0 1.0'
        with self.assertRaises(ValueError) as ar:
            wkt.loads(ls)
        self.assertEqual('Invalid WKT: `LINESTRING 0.0 1.0`',
                         str(ar.exception))

    def test_2d_srid1234(self):
        ls = 'SRID=1234;LINESTRING (0 -1, -2 -3, -4 5)'
        expected = dict(
            type='LineString',
            coordinates=[[0.0, -1.0], [-2.0, -3.0], [-4.0, 5.0]],
            meta=dict(srid=1234),
        )
        self.assertEqual(expected, wkt.loads(ls))


class PolygonDumpsTestCase(unittest.TestCase):

    def test_2d(self):
        poly = dict(type='Polygon', coordinates=[
            [[100.001, 0.001], [101.12345, 0.001], [101.001, 1.001],
             [100.001, 0.001]],
            [[100.201, 0.201], [100.801, 0.201], [100.801, 0.801],
             [100.201, 0.201]],
        ])
        expected = WKT['polygon']['2d']
        self.assertEqual(expected, wkt.dumps(poly, decimals=4))

    def test_3d(self):
        poly = dict(type='Polygon', coordinates=[
            [[100.0, 0.0, 3.1], [101.0, 0.0, 2.1], [101.0, 1.0, 1.1],
             [100.0, 0.0, 3.1]],
            [[100.2, 0.2, 3.1], [100.8, 0.2, 2.1], [100.8, 0.8, 1.1],
             [100.2, 0.2, 3.1]],
        ])
        expected = WKT['polygon']['3d']
        self.assertEqual(expected, wkt.dumps(poly, decimals=1))

    def test_4d(self):
        poly = dict(type='Polygon', coordinates=[
            [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [1, 2, 3, 4]]
        ])
        expected = WKT['polygon']['4d']
        self.assertEqual(expected, wkt.dumps(poly, decimals=0))

    def test_2d_srid2666(self):
        poly = dict(
            type='Polygon',
            coordinates=[
                [[100.001, 0.001], [101.12345, 0.001], [101.001, 1.001],
                 [100.001, 0.001]],
                [[100.201, 0.201], [100.801, 0.201], [100.801, 0.801],
                 [100.201, 0.201]],
            ],
            meta=dict(srid=2666),
        )
        expected = 'SRID=2666;' + WKT['polygon']['2d']
        self.assertEqual(expected, wkt.dumps(poly, decimals=4))


class PolygonLoadsTestCase(unittest.TestCase):

    def test_2d(self):
        poly = (
            'POLYGON ((100.001 0.001, 101.001 0.001, 101.001 1.001, '
            '100.001 0.001), '
            '(100.201 0.201, 100.801 0.201, 100.801 0.801, '
            '100.201 0.201))'
        )
        expected = dict(type='Polygon', coordinates=[
            [[100.001, 0.001], [101.001, 0.001], [101.001, 1.001],
             [100.001, 0.001]],
            [[100.201, 0.201], [100.801, 0.201], [100.801, 0.801],
             [100.201, 0.201]],
        ])
        self.assertEqual(expected, wkt.loads(poly))

    def test_3d(self):
        poly = (
            'POLYGON ((100.0 0.0 3.1, 101.0 0.0 2.1, 101.0 1.0 1.1, '
            '100.0 0.0 3.1), '
            '(100.2 0.2 3.1, 100.8 0.2 2.1, 100.8 0.8 1.1, 100.2 0.2 3.1))'
        )
        expected = dict(type='Polygon', coordinates=[
            [[100.0, 0.0, 3.1], [101.0, 0.0, 2.1], [101.0, 1.0, 1.1],
             [100.0, 0.0, 3.1]],
            [[100.2, 0.2, 3.1], [100.8, 0.2, 2.1], [100.8, 0.8, 1.1],
             [100.2, 0.2, 3.1]],
        ])
        self.assertEqual(expected, wkt.loads(poly))

    def test_4d(self):
        poly = 'POLYGON ((1 2 3 4, 5 6 7 8, 9 10 11 12, 1 2 3 4))'
        expected = dict(type='Polygon', coordinates=[
            [[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0],
             [9.0, 10.0, 11.0, 12.0], [1.0, 2.0, 3.0, 4.0]]
        ])
        self.assertEqual(expected, wkt.loads(poly))

    def test_raises_unmatched_paren(self):
        poly = 'POLYGON ((0.0 0.0, 1.0 4.0, 4.0 1.0, 0.0 0.0)'
        with self.assertRaises(ValueError) as ar:
            wkt.loads(poly)
        self.assertEqual(
            'Invalid WKT: `POLYGON ((0.0 0.0, 1.0 4.0, 4.0 1.0, 0.0 0.0)`',
            str(ar.exception)
        )

    def test_raises_invalid_wkt(self):
        poly = 'POLYGON 0.0 0.0, 1.0 4.0, 4.0 1.0, 0.0 0.0))'
        with self.assertRaises(ValueError) as ar:
            wkt.loads(poly)
        self.assertEqual(
            'Invalid WKT: `POLYGON 0.0 0.0, 1.0 4.0, 4.0 1.0, 0.0 0.0))`',
            str(ar.exception)
        )

    def test_2d_srid2666(self):
        poly = (
            'SRID=2666;POLYGON ((100.001 0.001, 101.001 0.001, 101.001 1.001, '
            '100.001 0.001), '
            '(100.201 0.201, 100.801 0.201, 100.801 0.801, '
            '100.201 0.201))'
        )
        expected = dict(
            type='Polygon',
            coordinates=[
                [[100.001, 0.001], [101.001, 0.001], [101.001, 1.001],
                 [100.001, 0.001]],
                [[100.201, 0.201], [100.801, 0.201], [100.801, 0.801],
                 [100.201, 0.201]],
            ],
            meta=dict(srid=2666),
        )
        self.assertEqual(expected, wkt.loads(poly))


class MultiPointLoadsTestCase(unittest.TestCase):

    def test_2d(self):
        mp = WKT['multipoint']['2d']
        expected = dict(type='MultiPoint', coordinates=[
            [100.0, 3.101], [101.0, 2.1], [3.14, 2.18],
        ])
        self.assertEqual(expected, wkt.loads(mp))

    def test_2d_alternate(self):
        # alternative style for representing a multipoint in WKT
        mp = 'MULTIPOINT (100.000 3.101, 101.000 2.100, 3.140 2.180)'
        expected = dict(type='MultiPoint', coordinates=[
            [100.0, 3.101], [101.0, 2.1], [3.14, 2.18],
        ])
        self.assertEqual(expected, wkt.loads(mp))

    def test_3d(self):
        mp = WKT['multipoint']['3d']
        expected = dict(type='MultiPoint', coordinates=[
            [100.0, 3.1, 1.0], [101.0, 2.1, 2.0], [3.14, 2.18, 3.0],
        ])
        self.assertEqual(expected, wkt.loads(mp))

    def test_4d(self):
        mp = WKT['multipoint']['4d']
        expected = dict(type='MultiPoint', coordinates=[
            [100.0, 3.1, 1.0, 0.0],
            [101.0, 2.1, 2.0, 0.0],
            [3.14, 2.18, 3.0, 0.0],
        ])
        self.assertEqual(expected, wkt.loads(mp))

    def test_2d_srid4326(self):
        mp = 'SRID=4326;' + WKT['multipoint']['2d']
        expected = dict(
            type='MultiPoint',
            coordinates=[[100.0, 3.101], [101.0, 2.1], [3.14, 2.18]],
            meta=dict(srid=4326),
        )
        self.assertEqual(expected, wkt.loads(mp))

    def test_malformed_wkt(self):
        mp = 'MULTIPOINT 0 1, 0 0'
        with self.assertRaises(ValueError) as ar:
            wkt.loads(mp)

        expected = 'Invalid WKT: `MULTIPOINT 0 1, 0 0`'
        self.assertEqual(expected, str(ar.exception))

    def test_malformed_wkt_misbalanced_parens(self):
        mp = 'MULTIPOINT ((0 0), (0 1)'
        with self.assertRaises(ValueError) as ar:
            wkt.loads(mp)

        expected = 'Invalid WKT: `MULTIPOINT ((0 0), (0 1)`'
        self.assertEqual(expected, str(ar.exception))


class MultiPointDumpsTestCase(unittest.TestCase):

    def test_2d(self):
        mp = dict(type='MultiPoint', coordinates=[
            [100.0, 3.101], [101.0, 2.1], [3.14, 2.18],
        ])
        expected = WKT['multipoint']['2d']
        self.assertEqual(expected, wkt.dumps(mp, decimals=3))

    def test_3d(self):
        mp = dict(type='MultiPoint', coordinates=[
            [100.0, 3.1, 1], [101.0, 2.1, 2], [3.14, 2.18, 3],
        ])
        expected = WKT['multipoint']['3d']
        self.assertEqual(expected, wkt.dumps(mp, decimals=2))

    def test_4d(self):
        mp = dict(type='MultiPoint', coordinates=[
            [100.0, 3.1, 1, 0], [101.0, 2.1, 2, 0], [3.14, 2.18, 3, 0],
        ])
        expected = WKT['multipoint']['4d']
        self.assertEqual(expected, wkt.dumps(mp, decimals=2))

    def test_2d_srid4326(self):
        mp = dict(
            type='MultiPoint',
            coordinates=[[100.0, 3.101], [101.0, 2.1], [3.14, 2.18]],
            meta=dict(srid=4326),
        )
        expected = 'SRID=4326;' + WKT['multipoint']['2d']
        self.assertEqual(expected, wkt.dumps(mp, decimals=3))


class MultiPolygonDumpsTestCase(unittest.TestCase):

    def test(self):
        mpoly = dict(type='MultiPolygon', coordinates=[
            [[[100.001, 0.001], [101.001, 0.001], [101.001, 1.001],
              [100.001, 0.001]],
             [[100.201, 0.201], [100.801, 0.201], [100.801, 0.801],
              [100.201, 0.201]]],
            [[[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0],
              [9.0, 10.0, 11.0, 12.0], [1.0, 2.0, 3.0, 4.0]]],
        ])
        expected = (
            'MULTIPOLYGON (((100.001 0.001, 101.001 0.001, 101.001 1.001, '
            '100.001 0.001), '
            '(100.201 0.201, 100.801 0.201, 100.801 0.801, '
            '100.201 0.201)), '
            '((1.000 2.000 3.000 4.000, 5.000 6.000 7.000 8.000, '
            '9.000 10.000 11.000 12.000, 1.000 2.000 3.000 4.000)))'
        )
        self.assertEqual(expected, wkt.dumps(mpoly, decimals=3))

    def test_srid4326(self):
        mpoly = dict(
            type='MultiPolygon',
            coordinates=[
                [[[100.001, 0.001], [101.001, 0.001], [101.001, 1.001],
                  [100.001, 0.001]],
                 [[100.201, 0.201], [100.801, 0.201], [100.801, 0.801],
                  [100.201, 0.201]]],
                [[[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0],
                  [9.0, 10.0, 11.0, 12.0], [1.0, 2.0, 3.0, 4.0]]],
            ],
            meta=dict(srid=4326),
        )
        expected = (
            'SRID=4326;MULTIPOLYGON (('
            '(100.001 0.001, 101.001 0.001, 101.001 1.001, 100.001 0.001), '
            '(100.201 0.201, 100.801 0.201, 100.801 0.801, 100.201 0.201)), '
            '((1.000 2.000 3.000 4.000, 5.000 6.000 7.000 8.000, '
            '9.000 10.000 11.000 12.000, 1.000 2.000 3.000 4.000)))'
        )
        self.assertEqual(expected, wkt.dumps(mpoly, decimals=3))


class MultiPolygonLoadsTestCase(unittest.TestCase):

    def test(self):
        mpoly = WKT['multipolygon']
        expected = dict(type='MultiPolygon', coordinates=[
            [[[100.001, 0.001], [101.001, 0.001], [101.001, 1.001],
              [100.001, 0.001]],
             [[100.201, 0.201], [100.801, 0.201], [100.801, 0.801],
              [100.201, 0.201]]],
            [[[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0],
              [9.0, 10.0, 11.0, 12.0], [1.0, 2.0, 3.0, 4.0]]],
        ])
        self.assertEqual(expected, wkt.loads(mpoly))

    def test_srid667(self):
        mpoly = 'SRID=667;' + WKT['multipolygon']
        expected = dict(
            type='MultiPolygon',
            coordinates=[
                [[[100.001, 0.001], [101.001, 0.001], [101.001, 1.001],
                  [100.001, 0.001]],
                 [[100.201, 0.201], [100.801, 0.201], [100.801, 0.801],
                  [100.201, 0.201]]],
                [[[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0],
                  [9.0, 10.0, 11.0, 12.0], [1.0, 2.0, 3.0, 4.0]]],
            ],
            meta=dict(srid=667),
        )
        self.assertEqual(expected, wkt.loads(mpoly))

    def test_malformed_wkt(self):
        mp = 'MULTIPOLYGON 0 1, 0 0'
        with self.assertRaises(ValueError) as ar:
            wkt.loads(mp)

        expected = 'Invalid WKT: `MULTIPOLYGON 0 1, 0 0`'
        self.assertEqual(expected, str(ar.exception))

    def test_malformed_wkt_misbalanced_parens(self):
        mp = (
            'MULTIPOLYGON (((0 0, 0 1, 1 1, 1 0, 0 0)), '
            '((0 0, 0 1, 1 1, 1 0, 0 0))'
        )
        with self.assertRaises(ValueError) as ar:
            wkt.loads(mp)

        expected = (
            'Invalid WKT: `MULTIPOLYGON (((0 0, 0 1, 1 1, 1 0, 0 0)), '
            '((0 0, 0 1, 1 1, 1 0, 0 0))`'
        )
        self.assertEqual(expected, str(ar.exception))


class MultiLineStringDumpsTestCase(unittest.TestCase):

    def test_2d(self):
        mlls = dict(type='MultiLineString', coordinates=[
            [[0.0, -1.0], [-2.0, -3.0], [-4.0, -5.0]],
            [[1.66, -31023.5], [10000.9999, 3.0], [100.9, 1.1],
             [0.0, 0.0]],
        ])
        expected = (
            'MULTILINESTRING ((0.000 -1.000, -2.000 -3.000, -4.000 -5.000), '
            '(1.660 -31023.500, 10001.000 3.000, 100.900 1.100, 0.000 0.000))'
        )
        self.assertEqual(expected, wkt.dumps(mlls, decimals=3))

    def test_3d(self):
        mlls = dict(type='MultiLineString', coordinates=[
            [[0.0, -1.0, 1.0], [-2.0, -3.0, 1.0], [-4.0, -5.0, 1.0]],
            [[1.66, -31023.5, 1.1], [10000.9999, 3.0, 2.2], [100.9, 1.1, 3.3],
             [0.0, 0.0, 4.4]],
        ])
        expected = (
            'MULTILINESTRING ((0.000 -1.000 1.000, -2.000 -3.000 1.000, '
            '-4.000 -5.000 1.000), '
            '(1.660 -31023.500 1.100, 10001.000 3.000 2.200, '
            '100.900 1.100 3.300, 0.000 0.000 4.400))'
        )
        self.assertEqual(expected, wkt.dumps(mlls, decimals=3))

    def test_4d(self):
        mlls = dict(type='MultiLineString', coordinates=[
            [[0.0, -1.0, 1.0, 0.0], [-2.0, -3.0, 1.0, 0.0],
             [-4.0, -5.0, 1.0, 0.0]],
            [[1.66, -31023.5, 1.1, 0.0], [10000.9999, 3.0, 2.2, 0.0],
             [100.9, 1.1, 3.3, 0.0], [0.0, 0.0, 4.4, 0.0]],
        ])
        expected = (
            'MULTILINESTRING ((0.00 -1.00 1.00 0.00, '
            '-2.00 -3.00 1.00 0.00, -4.00 -5.00 1.00 0.00), '
            '(1.66 -31023.50 1.10 0.00, 10001.00 3.00 2.20 0.00, '
            '100.90 1.10 3.30 0.00, 0.00 0.00 4.40 0.00))'
        )
        self.assertEqual(expected, wkt.dumps(mlls, decimals=2))

    def test_2d_srid4326(self):
        mlls = dict(
            type='MultiLineString',
            coordinates=[
                [[0.0, -1.0], [-2.0, -3.0], [-4.0, -5.0]],
                [[1.66, -31023.5], [10000.9999, 3.0], [100.9, 1.1],
                 [0.0, 0.0]],
            ],
            meta=dict(srid=4326),
        )
        expected = (
            'SRID=4326;MULTILINESTRING ('
            '(0.000 -1.000, -2.000 -3.000, -4.000 -5.000), '
            '(1.660 -31023.500, 10001.000 3.000, 100.900 1.100, 0.000 0.000))'
        )
        self.assertEqual(expected, wkt.dumps(mlls, decimals=3))


class MultiLineStringLoadsTestCase(unittest.TestCase):

    def test(self):
        mlls = WKT['multilinestring']
        expected = dict(
            type='MultiLineString',
            coordinates=[
                [[0.0, -1.0], [-2.0, -3.0], [-4.0, -5.0]],
                [[1.66, -31023.5, 1.1], [10000.9999, 3.0, 2.2],
                 [100.9, 1.1, 3.3], [0.0, 0.0, 4.4]],
            ]
        )
        self.assertEqual(expected, wkt.loads(mlls))

    def test_srid1234(self):
        mlls = 'SRID=1234;' + WKT['multilinestring']
        expected = dict(
            type='MultiLineString',
            coordinates=[
                [[0.0, -1.0], [-2.0, -3.0], [-4.0, -5.0]],
                [[1.66, -31023.5, 1.1], [10000.9999, 3.0, 2.2],
                 [100.9, 1.1, 3.3], [0.0, 0.0, 4.4]],
            ],
            meta=dict(srid=1234),
        )
        self.assertEqual(expected, wkt.loads(mlls))

    def test_malformed_wkt(self):
        mp = 'MULTILINESTRING 0 1, 0 0'
        with self.assertRaises(ValueError) as ar:
            wkt.loads(mp)

        expected = 'Invalid WKT: `MULTILINESTRING 0 1, 0 0`'
        self.assertEqual(expected, str(ar.exception))

    def test_malformed_wkt_misbalanced_parens(self):
        mp = 'MULTILINESTRING ((0 0, 0 1), (0 2, 2 2)'
        with self.assertRaises(ValueError) as ar:
            wkt.loads(mp)

        expected = 'Invalid WKT: `MULTILINESTRING ((0 0, 0 1), (0 2, 2 2)`'
        self.assertEqual(expected, str(ar.exception))


class GeometryCollectionDumpsTestCase(unittest.TestCase):

    def test_basic(self):
        gc = {
            'geometries': [
                {'coordinates': [0.0, 1.0], 'type': 'Point'},
                {'coordinates': [[-100.0, 0.0], [-101.0, -1.0]],
                 'type': 'LineString'},
                {'coordinates': [[[100.001, 0.001],
                                  [101.1235, 0.001],
                                  [101.001, 1.001],
                                  [100.001, 0.001]],
                                 [[100.201, 0.201],
                                  [100.801, 0.201],
                                  [100.801, 0.801],
                                  [100.201, 0.201]]],
                 'type': 'Polygon'},
                {'coordinates': [[100.0, 3.101], [101.0, 2.1], [3.14, 2.18]],
                 'type': 'MultiPoint'},
                {'coordinates': [[[0.0, -1.0], [-2.0, -3.0], [-4.0, -5.0]],
                                 [[1.66, -31023.5, 1.1],
                                  [10000.9999, 3.0, 2.2],
                                  [100.9, 1.1, 3.3],
                                  [0.0, 0.0, 4.4]]],
                 'type': 'MultiLineString'},
                {'coordinates': [[[[100.001, 0.001],
                                   [101.001, 0.001],
                                   [101.001, 1.001],
                                   [100.001, 0.001]],
                                  [[100.201, 0.201],
                                   [100.801, 0.201],
                                   [100.801, 0.801],
                                   [100.201, 0.201]]],
                                 [[[1.0, 2.0, 3.0, 4.0],
                                   [5.0, 6.0, 7.0, 8.0],
                                   [9.0, 10.0, 11.0, 12.0],
                                   [1.0, 2.0, 3.0, 4.0]]]],
                 'type': 'MultiPolygon'},
            ],
            'type': 'GeometryCollection',
        }
        expected = (
            'GEOMETRYCOLLECTION '
            '(POINT (0.000 1.000),'
            'LINESTRING (-100.000 0.000, -101.000 -1.000),'
            'POLYGON ((100.001 0.001, 101.124 0.001, 101.001 1.001, '
            '100.001 0.001), (100.201 0.201, 100.801 0.201, 100.801 0.801, '
            '100.201 0.201)),'
            'MULTIPOINT ((100.000 3.101), (101.000 2.100), (3.140 2.180)),'
            'MULTILINESTRING ((0.000 -1.000, -2.000 -3.000, -4.000 -5.000), '
            '(1.660 -31023.500 1.100, 10001.000 3.000 2.200, '
            '100.900 1.100 3.300, 0.000 0.000 4.400)),'
            'MULTIPOLYGON (((100.001 0.001, 101.001 0.001, 101.001 1.001, '
            '100.001 0.001), '
            '(100.201 0.201, 100.801 0.201, 100.801 0.801, 100.201 0.201)), '
            '((1.000 2.000 3.000 4.000, 5.000 6.000 7.000 8.000, '
            '9.000 10.000 11.000 12.000, 1.000 2.000 3.000 4.000))))'
        )
        self.assertEqual(expected, wkt.dumps(gc, decimals=3))

    def test_nested_gc(self):
        gc = {
            "type": "GeometryCollection",
            "geometries": [
                {
                    "type": "GeometryCollection",
                    "geometries": [
                        {
                            "type": "Point",
                            "coordinates": [
                                1.0,
                                2.0
                            ]
                        },
                        {
                            "type": "Point",
                            "coordinates": [
                                3.0,
                                4.0
                            ]
                        },
                    ],
                },
                {
                    "type": "Point",
                    "coordinates": [
                        5.0,
                        6.0
                    ],
                },
            ],
        }
        expected = (
            "GEOMETRYCOLLECTION (GEOMETRYCOLLECTION (POINT (1 2),POINT (3 4)),"
            "POINT (5 6))"
        )
        self.assertEqual(expected, wkt.dumps(gc, decimals=0))

    def test_srid26618(self):
        gc = {
            'geometries': [
                {'coordinates': [0.0, 1.0], 'type': 'Point'},
                {'coordinates': [[-100.0, 0.0], [-101.0, -1.0]],
                 'type': 'LineString'},
                {'coordinates': [[[100.001, 0.001],
                                  [101.1235, 0.001],
                                  [101.001, 1.001],
                                  [100.001, 0.001]],
                                 [[100.201, 0.201],
                                  [100.801, 0.201],
                                  [100.801, 0.801],
                                  [100.201, 0.201]]],
                 'type': 'Polygon'},
                {'coordinates': [[100.0, 3.101], [101.0, 2.1], [3.14, 2.18]],
                 'type': 'MultiPoint'},
                {'coordinates': [[[0.0, -1.0], [-2.0, -3.0], [-4.0, -5.0]],
                                 [[1.66, -31023.5, 1.1],
                                  [10000.9999, 3.0, 2.2],
                                  [100.9, 1.1, 3.3],
                                  [0.0, 0.0, 4.4]]],
                 'type': 'MultiLineString'},
                {'coordinates': [[[[100.001, 0.001],
                                   [101.001, 0.001],
                                   [101.001, 1.001],
                                   [100.001, 0.001]],
                                  [[100.201, 0.201],
                                   [100.801, 0.201],
                                   [100.801, 0.801],
                                   [100.201, 0.201]]],
                                 [[[1.0, 2.0, 3.0, 4.0],
                                   [5.0, 6.0, 7.0, 8.0],
                                   [9.0, 10.0, 11.0, 12.0],
                                   [1.0, 2.0, 3.0, 4.0]]]],
                 'type': 'MultiPolygon'},
            ],
            'type': 'GeometryCollection',
            'meta': dict(srid=26618),
        }
        expected = (
            'SRID=26618;GEOMETRYCOLLECTION '
            '(POINT (0.000 1.000),'
            'LINESTRING (-100.000 0.000, -101.000 -1.000),'
            'POLYGON ((100.001 0.001, 101.124 0.001, 101.001 1.001, '
            '100.001 0.001), (100.201 0.201, 100.801 0.201, 100.801 0.801, '
            '100.201 0.201)),'
            'MULTIPOINT ((100.000 3.101), (101.000 2.100), (3.140 2.180)),'
            'MULTILINESTRING ((0.000 -1.000, -2.000 -3.000, -4.000 -5.000), '
            '(1.660 -31023.500 1.100, 10001.000 3.000 2.200, '
            '100.900 1.100 3.300, 0.000 0.000 4.400)),'
            'MULTIPOLYGON (((100.001 0.001, 101.001 0.001, 101.001 1.001, '
            '100.001 0.001), '
            '(100.201 0.201, 100.801 0.201, 100.801 0.801, 100.201 0.201)), '
            '((1.000 2.000 3.000 4.000, 5.000 6.000 7.000 8.000, '
            '9.000 10.000 11.000 12.000, 1.000 2.000 3.000 4.000))))'
        )
        self.assertEqual(expected, wkt.dumps(gc, decimals=3))

    def test_with_empty_component_simple(self):
        gc = {
            'type': 'GeometryCollection',
            'geometries': [
                {'type': 'Point', 'coordinates': [0, 0]},
                {'type': 'Point', 'coordinates': []}
            ]
        }

        expected = 'GEOMETRYCOLLECTION (POINT (0 0),POINT EMPTY)'

        self.assertEqual(expected, wkt.dumps(gc, decimals=0))

    def test_with_empty_component(self):
        # Example from https://github.com/geomet/geomet/issues/49
        gc = {
            'type': 'GeometryCollection',
            'geometries': [
                {
                    'type': 'Polygon',
                    'coordinates': [
                        [
                            [27.0, 25.0],
                            [102.0, 36.0],
                            [102.0, 46.0],
                            [92.0, 61.0],
                            [13.0, 41.0],
                            [16.0, 30.0],
                            [27.0, 25.0]
                        ]
                    ]
                },
                {'type': 'LineString', 'coordinates': []}
            ]}

        expected = (
            'GEOMETRYCOLLECTION ('
            'POLYGON ((27 25, 102 36, 102 46, 92 61, 13 41, 16 30, 27 25)),'
            'LINESTRING EMPTY)'
        )

        self.assertEqual(expected, wkt.dumps(gc, decimals=0))

    def test_empty_component_with_srid(self):
        gc = {
            'type': 'GeometryCollection',
            'meta': {'srid': 4326},
            'geometries': [
                {'type': 'Point', 'coordinates': []}
            ]
        }

        expected = 'SRID=4326;GEOMETRYCOLLECTION (POINT EMPTY)'

        self.assertEqual(expected, wkt.dumps(gc))

    def test_all_types_empty(self):
        gc = {
            'type': 'GeometryCollection',
            'geometries': [
                {'geometries': [], 'type': 'GeometryCollection'},
                {'coordinates': [], 'type': 'LineString'},
                {'coordinates': [], 'type': 'MultiLineString'},
                {'coordinates': [], 'type': 'MultiPoint'},
                {'coordinates': [], 'type': 'MultiPolygon'},
                {'coordinates': [], 'type': 'Point'},
                {'coordinates': [], 'type': 'Polygon'}
            ]
        }

        expected = 'GEOMETRYCOLLECTION (%s)' % ','.join(
            '%s EMPTY' % typ for typ in sorted(
                wkt._type_map_caps_to_mixed.keys()))

        self.assertEqual(expected, wkt.dumps(gc))


class GeometryCollectionLoadsTestCase(unittest.TestCase):

    def test_basic_gc(self):
        gc = 'GEOMETRYCOLLECTION (%s,%s,%s,%s,%s,%s)' % (
            WKT['point']['2d'],
            WKT['linestring']['2d'],
            WKT['polygon']['2d'],
            WKT['multipoint']['2d'],
            WKT['multilinestring'],
            WKT['multipolygon'],
        )
        expected = {
            'geometries': [
                {'coordinates': [0.0, 1.0], 'type': 'Point'},
                {'coordinates': [[-100.0, 0.0], [-101.0, -1.0]],
                 'type': 'LineString'},
                {'coordinates': [[[100.001, 0.001],
                                  [101.1235, 0.001],
                                  [101.001, 1.001],
                                  [100.001, 0.001]],
                                 [[100.201, 0.201],
                                  [100.801, 0.201],
                                  [100.801, 0.801],
                                  [100.201, 0.201]]],
                 'type': 'Polygon'},
                {'coordinates': [[100.0, 3.101], [101.0, 2.1], [3.14, 2.18]],
                 'type': 'MultiPoint'},
                {'coordinates': [[[0.0, -1.0], [-2.0, -3.0], [-4.0, -5.0]],
                                 [[1.66, -31023.5, 1.1],
                                  [10000.9999, 3.0, 2.2],
                                  [100.9, 1.1, 3.3],
                                  [0.0, 0.0, 4.4]]],
                 'type': 'MultiLineString'},
                {'coordinates': [[[[100.001, 0.001],
                                   [101.001, 0.001],
                                   [101.001, 1.001],
                                   [100.001, 0.001]],
                                  [[100.201, 0.201],
                                   [100.801, 0.201],
                                   [100.801, 0.801],
                                   [100.201, 0.201]]],
                                 [[[1.0, 2.0, 3.0, 4.0],
                                   [5.0, 6.0, 7.0, 8.0],
                                   [9.0, 10.0, 11.0, 12.0],
                                   [1.0, 2.0, 3.0, 4.0]]]],
                 'type': 'MultiPolygon'},
            ],
            'type': 'GeometryCollection',
        }
        self.assertEqual(expected, wkt.loads(gc))

    def test_nested_gc(self):
        # Test the parsing of a nested geometry collection.
        gc = (
            "GEOMETRYCOLLECTION(GEOMETRYCOLLECTION(POINT(1 2), POINT(3 4)), "
            "POINT(5 6))"
        )
        expected = {
            "type": "GeometryCollection",
            "geometries": [
                {
                    "type": "GeometryCollection",
                    "geometries": [
                        {
                            "type": "Point",
                            "coordinates": [
                                1.0,
                                2.0
                            ]
                        },
                        {
                            "type": "Point",
                            "coordinates": [
                                3.0,
                                4.0
                            ]
                        },
                    ],
                },
                {
                    "type": "Point",
                    "coordinates": [
                        5.0,
                        6.0
                    ],
                },
            ],
        }
        self.assertEqual(expected, wkt.loads(gc))

    def test_srid662(self):
        gc = 'SRID=662;GEOMETRYCOLLECTION (%s,%s,%s,%s,%s,%s)' % (
            WKT['point']['2d'],
            WKT['linestring']['2d'],
            WKT['polygon']['2d'],
            WKT['multipoint']['2d'],
            WKT['multilinestring'],
            WKT['multipolygon'],
        )
        expected = {
            'geometries': [
                {'coordinates': [0.0, 1.0], 'type': 'Point'},
                {'coordinates': [[-100.0, 0.0], [-101.0, -1.0]],
                 'type': 'LineString'},
                {'coordinates': [[[100.001, 0.001],
                                  [101.1235, 0.001],
                                  [101.001, 1.001],
                                  [100.001, 0.001]],
                                 [[100.201, 0.201],
                                  [100.801, 0.201],
                                  [100.801, 0.801],
                                  [100.201, 0.201]]],
                 'type': 'Polygon'},
                {'coordinates': [[100.0, 3.101], [101.0, 2.1], [3.14, 2.18]],
                 'type': 'MultiPoint'},
                {'coordinates': [[[0.0, -1.0], [-2.0, -3.0], [-4.0, -5.0]],
                                 [[1.66, -31023.5, 1.1],
                                  [10000.9999, 3.0, 2.2],
                                  [100.9, 1.1, 3.3],
                                  [0.0, 0.0, 4.4]]],
                 'type': 'MultiLineString'},
                {'coordinates': [[[[100.001, 0.001],
                                   [101.001, 0.001],
                                   [101.001, 1.001],
                                   [100.001, 0.001]],
                                  [[100.201, 0.201],
                                   [100.801, 0.201],
                                   [100.801, 0.801],
                                   [100.201, 0.201]]],
                                 [[[1.0, 2.0, 3.0, 4.0],
                                   [5.0, 6.0, 7.0, 8.0],
                                   [9.0, 10.0, 11.0, 12.0],
                                   [1.0, 2.0, 3.0, 4.0]]]],
                 'type': 'MultiPolygon'},
            ],
            'type': 'GeometryCollection',
            'meta': dict(srid=662),
        }
        self.assertEqual(expected, wkt.loads(gc))

    def test_with_empty_component_simple(self):
        gc = 'GEOMETRYCOLLECTION (POINT (0 0), POINT EMPTY)'

        expected = {
            'type': 'GeometryCollection',
            'geometries': [
                {'type': 'Point', 'coordinates': [0, 0]},
                {'type': 'Point', 'coordinates': []}
            ]
        }

        self.assertEqual(expected, wkt.loads(gc))

    def test_with_empty_component(self):
        # Example from https://github.com/geomet/geomet/issues/49
        gc = (
            'GEOMETRYCOLLECTION ('
            'POLYGON((27 25,102 36,102 46,92 61,13 41,16 30,27 25)),'
            'LINESTRING EMPTY)'
        )

        expected = {
            'type': 'GeometryCollection',
            'geometries': [
                {
                    'type': 'Polygon',
                    'coordinates': [
                        [
                            [27.0, 25.0],
                            [102.0, 36.0],
                            [102.0, 46.0],
                            [92.0, 61.0],
                            [13.0, 41.0],
                            [16.0, 30.0],
                            [27.0, 25.0]
                        ]
                    ]
                },
                {'type': 'LineString', 'coordinates': []}
            ]}

        self.assertEqual(expected, wkt.loads(gc))

    def test_empty_component_with_srid(self):
        gc = 'SRID=4326;GEOMETRYCOLLECTION (POINT EMPTY)'

        expected = {
            'type': 'GeometryCollection',
            'meta': {'srid': 4326},
            'geometries': [
                {'type': 'Point', 'coordinates': []}
            ]
        }

        self.assertEqual(expected, wkt.loads(gc))

    def test_all_types_empty(self):
        gc = 'GEOMETRYCOLLECTION (%s)' % ','.join(
            '%s EMPTY' % typ for typ in sorted(
                wkt._type_map_caps_to_mixed.keys()))

        expected = {
            'type': 'GeometryCollection',
            'geometries': [
                {'geometries': [], 'type': 'GeometryCollection'},
                {'coordinates': [], 'type': 'LineString'},
                {'coordinates': [], 'type': 'MultiLineString'},
                {'coordinates': [], 'type': 'MultiPoint'},
                {'coordinates': [], 'type': 'MultiPolygon'},
                {'coordinates': [], 'type': 'Point'},
                {'coordinates': [], 'type': 'Polygon'}
            ]
        }
        self.assertEqual(expected, wkt.loads(gc))

    def test_malformed_wkt(self):
        mp = 'GEOMETRYCOLLECTION 0 1, 0 0'
        with self.assertRaises(ValueError) as ar:
            wkt.loads(mp)

        expected = 'Invalid WKT: `GEOMETRYCOLLECTION 0 1, 0 0`'
        self.assertEqual(expected, str(ar.exception))

    def test_malformed_wkt_no_ending_paren(self):
        mp = 'GEOMETRYCOLLECTION (POINT EMPTY'
        with self.assertRaises(ValueError) as ar:
            wkt.loads(mp)

        expected = 'Invalid WKT: `GEOMETRYCOLLECTION (POINT EMPTY`'
        self.assertEqual(expected, str(ar.exception))


class TestRoundAndPad(unittest.TestCase):
    def test(self):
        test_cases = [
            [(-1.000000000000000, 16), '-1.' + '0' * 16],
            [(-83.2496395, 16), '-83.2496395000000000'],
            [(35.917330500000006, 16), '35.9173305000000060'],
            [(6e-6, 16), '0.0000060000000000'],
            [(1e16, 3), '10000000000000000.000'],
            [(3.14e16, 3), '31400000000000000.000'],
            [(3.14e-16, 18), '0.000000000000000314'],
        ]

        for args, expected in test_cases:
            self.assertEqual(expected, wkt._round_and_pad(*args))


class TestMisc(unittest.TestCase):
    def test_assert_next_token(self):
        gen = (letter for letter in 'abcd')
        next(gen)

        wkt._assert_next_token(gen, 'b')

    def test_assert_next_token_raises(self):
        gen = (letter for letter in 'abcd')

        with self.assertRaises(ValueError) as ar:
            wkt._assert_next_token(gen, 'b')

        expected = 'Expected "b" but found "a"'
        self.assertEqual(expected, str(ar.exception))
