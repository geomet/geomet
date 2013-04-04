import unittest

from geomet import wkb

EXP_WKB_FMT = '%(endian)s%(type)s%(data)s'


class WKBTestCase(unittest.TestCase):

    def test_unsupported_geom_type(self):
        geom = dict(type='Tetrahedron', coordinates=[])
        with self.assertRaises(ValueError) as ar:
            wkb.dumps(geom)
        self.assertEqual("Unsupported geometry type 'Tetrahedron'",
                         ar.exception.message)



class PointTestCase(unittest.TestCase):

    def test_dumps_point_2d(self):
        # Tests a typical 2D Point case:
        pt = dict(type='Point', coordinates=[0.0, 1.0])
        expected = EXP_WKB_FMT
        expected %= dict(
            endian='\x01',
            type='\x01\x00\x00\x00',
            data=('\x00\x00\x00\x00\x00\x00\x00\x00'
                  '\x00\x00\x00\x00\x00\x00\xf0?'),
        )
        self.assertEqual(expected, wkb.dumps(pt, big_endian=False))

    def test_dumps_point_z(self):
        # Test for an XYZ Point:
        pt = dict(type='Point', coordinates=[0.0, 1.0, 2.0])

        data=('\x00\x00\x00\x00\x00\x00\x00\x00'
              '?\xf0\x00\x00\x00\x00\x00\x00'
              '@\x00\x00\x00\x00\x00\x00\x00')

        expected = EXP_WKB_FMT
        expected %= dict(
            endian='\x00',
            type='\x00\x00\x10\x01',
            data=data,
        )
        self.assertEqual(expected, wkb.dumps(pt, big_endian=True, dims='Z'))

    def test_dumps_point_m(self):
        # Test for an XYM Point:
        pt = dict(type='Point', coordinates=[0.0, 1.0, 2.0])

        data=('\x00\x00\x00\x00\x00\x00\x00\x00'
              '\x00\x00\x00\x00\x00\x00\xf0?'
              '\x00\x00\x00\x00\x00\x00\x00@')

        expected = EXP_WKB_FMT
        expected %= dict(
            endian='\x01',
            type='\x01\x20\x00\x00',
            data=data,
        )
        self.assertEqual(expected, wkb.dumps(pt, big_endian=False, dims='M'))

    def test_dumps_point_4d(self):
        # Test for an XYZM Point:
        pt = dict(type='Point', coordinates=[0.0, 1.0, 2.0, 4.0])

        data=('\x00\x00\x00\x00\x00\x00\x00\x00'
              '\x00\x00\x00\x00\x00\x00\xf0?'
              '\x00\x00\x00\x00\x00\x00\x00@'
              '\x00\x00\x00\x00\x00\x00\x10@')

        expected = EXP_WKB_FMT
        expected %= dict(
            endian='\x01',
            type='\x01\x30\x00\x00',
            data=data,
        )
        self.assertEqual(expected, wkb.dumps(pt, big_endian=False, dims='ZM'))

    def test_loads_point_2d(self):
        pt = (
            '\x01'  # little endian
            '\x01\x00\x00\x00'  # type
            '\x00\x00\x00\x00\x00\x00\x00\x00'  # 0.0
            '\x00\x00\x00\x00\x00\x00\xf0?'  # 1.0
        )

        expected = dict(type='Point', coordinates=[0.0, 1.0])
        self.assertEqual(expected, wkb.loads(pt))
