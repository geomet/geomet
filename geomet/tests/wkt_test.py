import unittest

from geomet import wkt


class WKTTestCase(unittest.TestCase):

    def test_unsupported_geom_type(self):
        geom = dict(type='Tetrahedron', coordinates=[])
        with self.assertRaises(ValueError) as ar:
            wkt.dumps(geom)
        self.assertEqual("Unsupported geometry type 'Tetrahedron'",
                         ar.exception.message)


class PointTestCase(unittest.TestCase):

    def test_dumps_point_2d(self):
        # Tests a typical 2D Point case:
        pt = dict(type='Point', coordinates=[0.0, 1.0])
        expected = 'POINT(0.0000000000000000 1.0000000000000000)'
        self.assertEqual(expected, wkt.dumps(pt))

    def test_dumps_point_3d(self):
        # Test for an XYZ/XYM Point:
        pt = dict(type='Point', coordinates=[0.0, 1.0, 2.0])
        expected = (
            'POINT(0.0000000000000000 1.0000000000000000 2.0000000000000000)'
        )
        self.assertEqual(expected, wkt.dumps(pt))

    def test_dumps_point_4d(self):
        # Test for an XYZM Point:
        pt = dict(type='Point', coordinates=[0.0, 1.0, 2.0, 4.0])
        expected = (
            'POINT(0.0000000000000000 1.0000000000000000 2.0000000000000000 '
            '4.0000000000000000)'
        )
        self.assertEqual(expected, wkt.dumps(pt))

    def test_dumps_point_6_decimals(self):
        pt = dict(type='Point', coordinates=[-10, -77])
        expected = 'POINT(-10.000000 -77.000000)'
        self.assertEqual(expected, wkt.dumps(pt, decimals=6))

    def test_loads_point_2d(self):
        pt = 'POINT(0.0000000000000000 1.0000000000000000)'
        expected = dict(type='Point', coordinates=[0.0, 1.0])
        self.assertEqual(expected, wkt.loads(pt))

    def test_loads_point_raises_unmatched_paren(self):
        pt = 'POINT(0.0 1.0'
        with self.assertRaises(ValueError) as ar:
            wkt.loads(pt)
        self.assertEqual('Invalid WKT: `POINT(0.0 1.0`',
                         ar.exception.message)

    def test_loads_point_raises_invalid_wkt(self):
        pt = 'POINT 0.0 1.0'
        with self.assertRaises(ValueError) as ar:
            wkt.loads(pt)
        self.assertEqual('Invalid WKT: `POINT 0.0 1.0`', ar.exception.message)


class LineStringTestCase(unittest.TestCase):

    def test_dumps_linestring_2d(self):
        # Test a typical 2D LineString case:
        ls = dict(type='LineString', coordinates=[[100.0, 0.0], [101.0, 1.0]])
        expected = (
            'LINESTRING(100.0000000000000000 0.0000000000000000, '
            '101.0000000000000000 1.0000000000000000)'
        )
        self.assertEqual(expected, wkt.dumps(ls))

    def test_dumps_linestring_3d(self):
        ls = dict(type='LineString', coordinates=[[100.0, 0.0, -60.0],
                                                  [101.0, 1.0, -65.25]])
        expected = (
            'LINESTRING('
            '100.0000000000000000 0.0000000000000000 -60.0000000000000000, '
            '101.0000000000000000 1.0000000000000000 -65.2500000000000000)'
        )
        self.assertEqual(expected, wkt.dumps(ls))

    def test_dumps_linestring_4d(self):
        ls = dict(type='LineString', coordinates=[[100.0, 0.0, -60.0, 0.1],
                                                  [101.0, 1.0, -65.25, 0.2]])
        expected = (
            'LINESTRING('
            '100.0000000000000000 0.0000000000000000 -60.0000000000000000 '
            '0.1000000000000000, '
            '101.0000000000000000 1.0000000000000000 -65.2500000000000000 '
            '0.2000000000000000)'
        )
        self.assertEqual(expected, wkt.dumps(ls))

    def test_dumps_linestring_3_decimals(self):
        ls = dict(type='LineString', coordinates=[[100.0, 0.0], [101.0, 1.0]])
        expected = 'LINESTRING(100.000 0.000, 101.000 1.000)'
        self.assertEqual(expected, wkt.dumps(ls, decimals=3))
