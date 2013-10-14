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
WKT['multipolygon'] = (
    'MULTIPOLYGON (((100.001 0.001, 101.001 0.001, 101.001 1.001, '
    '100.001 0.001), '
    '(100.201 0.201, 100.801 0.201, 100.801 0.801, '
    '100.201 0.201)), ((1 2 3 4, 5 6 7 8, 9 10 11 12, 1 2 3 4)))'
)
WKT['multilinestring'] = (
    'MULTILINESTRING ((0 -1, -2 -3, -4 -5), '
    '(1.66 -31023.5 1.1, 10000.9999 3.0 2.2, 100.9 1.1 3.3, 0 0 4.4))'
)

GEOJSON = {}


class WKTTestCase(unittest.TestCase):

    def test_unsupported_geom_type(self):
        geom = dict(type='Tetrahedron', coordinates=[])
        with self.assertRaises(ValueError) as ar:
            wkt.dumps(geom)
        self.assertEqual("Unsupported geometry type 'Tetrahedron'",
                         ar.exception.message)


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
                         ar.exception.message)

    def test_raises_invalid_wkt(self):
        pt = 'POINT 0.0 1.0'
        with self.assertRaises(ValueError) as ar:
            wkt.loads(pt)
        self.assertEqual('Invalid WKT: `POINT 0.0 1.0`', ar.exception.message)


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
                         ar.exception.message)

    def test_raises_invalid_wkt(self):
        ls = 'LINESTRING 0.0 1.0'
        with self.assertRaises(ValueError) as ar:
            wkt.loads(ls)
        self.assertEqual('Invalid WKT: `LINESTRING 0.0 1.0`',
                         ar.exception.message)


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
            ar.exception.message
        )

    def test_raises_invalid_wkt(self):
        poly = 'POLYGON 0.0 0.0, 1.0 4.0, 4.0 1.0, 0.0 0.0))'
        with self.assertRaises(ValueError) as ar:
            wkt.loads(poly)
        self.assertEqual(
            'Invalid WKT: `POLYGON 0.0 0.0, 1.0 4.0, 4.0 1.0, 0.0 0.0))`',
            ar.exception.message
        )


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


class MultiLineStringDumpsTestCase(unittest.TestCase):

    def test(self): pass


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


class GeometryCollectionDumpsTestCase(unittest.TestCase):

    def test(self): pass


class GeometryCollectionLoadsTestCase(unittest.TestCase):

    def test(self):
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
