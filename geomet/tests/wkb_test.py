import unittest

from geomet import wkb


class WKBTestCase(unittest.TestCase):

    def test_unsupported_geom_type(self):
        geom = dict(type='Tetrahedron', coordinates=[])
        with self.assertRaises(ValueError) as ar:
            wkb.dumps(geom)
        self.assertEqual("Unsupported geometry type 'Tetrahedron'",
                         str(ar.exception))


class PointDumpsTestCase(unittest.TestCase):

    def test_2d(self):
        # Tests a typical 2D Point case:
        pt = dict(type='Point', coordinates=[0.0, 1.0])

        expected = (
            b'\x01'  # little endian
            b'\x01\x00\x00\x00'  # type
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\xf0?'
        )

        self.assertEqual(expected, wkb.dumps(pt, big_endian=False))

    def test_3d(self):
        # Test for an XYZ Point:
        pt = dict(type='Point', coordinates=[0.0, 1.0, 2.0])
        # Note that a 3d point could either be a XYZ or XYM type.
        # For simplicity, we always assume XYZ.

        expected = (
            b'\x00'  # big endian
            b'\x00\x00\x10\x01'  # type
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'?\xf0\x00\x00\x00\x00\x00\x00'
            b'@\x00\x00\x00\x00\x00\x00\x00'
        )

        self.assertEqual(expected, wkb.dumps(pt, big_endian=True))

    def test_4d(self):
        # Test for an XYZM Point:
        pt = dict(type='Point', coordinates=[0.0, 1.0, 2.0, 4.0])

        expected = (
            b'\x01'  # little endian
            b'\x01\x30\x00\x00'  # type
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\xf0?'
            b'\x00\x00\x00\x00\x00\x00\x00@'
            b'\x00\x00\x00\x00\x00\x00\x10@'
        )

        self.assertEqual(expected, wkb.dumps(pt, big_endian=False))


class PointLoadsTestCase(unittest.TestCase):

    def test_2d(self):
        pt = (
            b'\x01'  # little endian
            b'\x01\x00\x00\x00'  # type
            b'\x00\x00\x00\x00\x00\x00\x00\x00'  # 0.0
            b'\x00\x00\x00\x00\x00\x00\xf0?'  # 1.0
        )

        expected = dict(type='Point', coordinates=[0.0, 1.0])
        self.assertEqual(expected, wkb.loads(pt))

    def test_z(self):
        pt = (
            b'\x00'  # big endian
            b'\x00\x00\x10\x01'  # type
            b'@\x01\x99\x99\x99\x99\x99\x9a'
            b'@\x11\x99\x99\x99\x99\x99\x9a'
            b'@\x08\xcc\xcc\xcc\xcc\xcc\xcd'
        )
        expected = dict(type='Point', coordinates=[2.2, 4.4, 3.1])
        self.assertEqual(expected, wkb.loads(pt))

    def test_m(self):
        pt = (
            b'\x00'  # big endian
            b'\x00\x00\x20\x01'  # type
            b'@\x01\x99\x99\x99\x99\x99\x9a'
            b'@\x11\x99\x99\x99\x99\x99\x9a'
            b'@\x08\xcc\xcc\xcc\xcc\xcc\xcd'
        )

        # The generated GeoJSON is treated as XYZM, sidestep the ambiguity
        # created by XYM and XYZ geometries. The default value for Z is set to
        # 0.0.
        expected = dict(type='Point', coordinates=[2.2, 4.4, 0.0, 3.1])
        self.assertEqual(expected, wkb.loads(pt))

    def test_zm(self):
        pt = (
            b'\x00'  # big endian
            b'\x00\x00\x30\x01'  # type
            b'@\x01\x99\x99\x99\x99\x99\x9a'
            b'@\x11\x99\x99\x99\x99\x99\x9a'
            b'@\x08\xcc\xcc\xcc\xcc\xcc\xcd'
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
        )
        expected = dict(type='Point', coordinates=[2.2, 4.4, 3.1, 0.0])
        self.assertEqual(expected, wkb.loads(pt))


class LineStringDumpsTestCase(unittest.TestCase):

    def test_2d(self):
        linestring = dict(type='LineString', coordinates=[[2.2, 4.4],
                                                          [3.1, 5.1]])
        expected = (
            b'\x00'  # big endian
            b'\x00\x00\x00\x02'  # type
            b'@\x01\x99\x99\x99\x99\x99\x9a'  # 2.2
            b'@\x11\x99\x99\x99\x99\x99\x9a'  # 4.4
            b'@\x08\xcc\xcc\xcc\xcc\xcc\xcd'  # 3.1
            b'@\x14ffffff'                    # 5.1
        )

        self.assertEqual(expected, wkb.dumps(linestring))

    def test_3d(self):
        linestring = dict(type='LineString', coordinates=[[2.2, 4.4, 10.0],
                                                          [3.1, 5.1, 20.0]])
        expected = (
            b'\x01'  # little endian
            b'\x02\x10\x00\x00'  # type
            b'\x9a\x99\x99\x99\x99\x99\x01@'  # 2.2
            b'\x9a\x99\x99\x99\x99\x99\x11@'  # 4.4
            b'\x00\x00\x00\x00\x00\x00$@'     # 10.0
            b'\xcd\xcc\xcc\xcc\xcc\xcc\x08@'  # 3.1
            b'ffffff\x14@'                    # 5.1
            b'\x00\x00\x00\x00\x00\x004@'     # 20.0
        )

        self.assertEqual(expected, wkb.dumps(linestring, big_endian=False))

    def test_4d(self):
        linestring = dict(type='LineString',
                          coordinates=[[2.2, -4.4, -10.0, 0.1],
                                       [-3.1, 5.1, 20.0, -0.9]])

        expected = (
            b'\x00'  # big endian
            b'\x00\x00\x30\x02'  # type
            b'@\x01\x99\x99\x99\x99\x99\x9a'     # 2.2
            b'\xc0\x11\x99\x99\x99\x99\x99\x9a'  # -4.4
            b'\xc0$\x00\x00\x00\x00\x00\x00'     # -10.0
            b'?\xb9\x99\x99\x99\x99\x99\x9a'     # 0.1
            b'\xc0\x08\xcc\xcc\xcc\xcc\xcc\xcd'  # -3.1
            b'@\x14ffffff'                       # 5.1
            b'@4\x00\x00\x00\x00\x00\x00'        # 20.0
            b'\xbf\xec\xcc\xcc\xcc\xcc\xcc\xcd'  # -0.9
        )

        self.assertEqual(expected, wkb.dumps(linestring))


class LineStringLoadsTestCase(unittest.TestCase):

    def test_2d(self):
        linestring = (
            b'\x00'  # big endian
            b'\x00\x00\x00\x02'
            b'@\x01\x99\x99\x99\x99\x99\x9a'  # 2.2
            b'@\x11\x99\x99\x99\x99\x99\x9a'  # 4.4
            b'@\x08\xcc\xcc\xcc\xcc\xcc\xcd'  # 3.1
            b'@\x14ffffff'                    # 5.1
        )
        expected = dict(type='LineString', coordinates=[[2.2, 4.4],
                                                        [3.1, 5.1]])

        self.assertEqual(expected, wkb.loads(linestring))

    def test_z(self):
        linestring = (
            b'\x01'  # little endian
            b'\x02\x10\x00\x00'
            b'\x9a\x99\x99\x99\x99\x99\x01@'  # 2.2
            b'\x9a\x99\x99\x99\x99\x99\x11@'  # 4.4
            b'\x00\x00\x00\x00\x00\x00$@'     # 10.0
            b'\xcd\xcc\xcc\xcc\xcc\xcc\x08@'  # 3.1
            b'ffffff\x14@'                    # 5.1
            b'\x00\x00\x00\x00\x00\x004@'     # 20.0
        )
        expected = dict(type='LineString', coordinates=[[2.2, 4.4, 10.0],
                                                        [3.1, 5.1, 20.0]])

        self.assertEqual(expected, wkb.loads(linestring))

    def test_m(self):
        linestring = (
            b'\x01'  # little endian
            b'\x02\x20\x00\x00'
            b'\x9a\x99\x99\x99\x99\x99\x01@'  # 2.2
            b'\x9a\x99\x99\x99\x99\x99\x11@'  # 4.4
            b'\x00\x00\x00\x00\x00\x00$@'     # 10.0
            b'\xcd\xcc\xcc\xcc\xcc\xcc\x08@'  # 3.1
            b'ffffff\x14@'                    # 5.1
            b'\x00\x00\x00\x00\x00\x004@'     # 20.0
        )
        expected = dict(type='LineString', coordinates=[[2.2, 4.4, 0.0, 10.0],
                                                        [3.1, 5.1, 0.0, 20.0]])

        self.assertEqual(expected, wkb.loads(linestring))

    def test_zm(self):
        linestring = (
            b'\x00'  # big endian
            b'\x00\x00\x30\x02'
            b'@\x01\x99\x99\x99\x99\x99\x9a'     # 2.2
            b'\xc0\x11\x99\x99\x99\x99\x99\x9a'  # -4.4
            b'\xc0$\x00\x00\x00\x00\x00\x00'     # -10.0
            b'?\xb9\x99\x99\x99\x99\x99\x9a'     # 0.1
            b'\xc0\x08\xcc\xcc\xcc\xcc\xcc\xcd'  # -3.1
            b'@\x14ffffff'                       # 5.1
            b'@4\x00\x00\x00\x00\x00\x00'        # 20.0
            b'\xbf\xec\xcc\xcc\xcc\xcc\xcc\xcd'  # -0.9
        )
        expected = dict(type='LineString',
                        coordinates=[[2.2, -4.4, -10.0, 0.1],
                                     [-3.1, 5.1, 20.0, -0.9]])

        self.assertEqual(expected, wkb.loads(linestring))


class PolygonDumpsTestCase(unittest.TestCase):

    def test_2d(self):
        poly = dict(type='Polygon', coordinates=[
            [[100.001, 0.001], [101.12345, 0.001], [101.001, 1.001],
             [100.001, 0.001]],
            [[100.201, 0.201], [100.801, 0.201], [100.801, 0.801],
             [100.201, 0.201]],
        ])
        expected = (
            b'\x00'
            b'\x00\x00\x00\x03'  # type
            # number of rings, 4 byte int
            b'\x00\x00\x00\x02'
            # number of verts in ring (4)
            b'\x00\x00\x00\x04'
            # coords
            b'@Y\x00\x10bM\xd2\xf2'     # 100.001
            b'?PbM\xd2\xf1\xa9\xfc'     # 0.001
            b'@YG\xe6\x9a\xd4,='        # 101.12345
            b'?PbM\xd2\xf1\xa9\xfc'     # 0.001
            b'@Y@\x10bM\xd2\xf2'        # 101.001
            b'?\xf0\x04\x18\x93t\xbcj'  # 1.001
            b'@Y\x00\x10bM\xd2\xf2'     # 100.001
            b'?PbM\xd2\xf1\xa9\xfc'     # 0.001
            # number of verts in ring (4)
            b'\x00\x00\x00\x04'
            # coords
            b'@Y\x0c\xdd/\x1a\x9f\xbe'     # 100.201
            b'?\xc9\xba^5?|\xee'           # 0.201
            b'@Y3C\x95\x81\x06%'           # 100.801
            b'?\xc9\xba^5?|\xee'           # 0.201
            b'@Y3C\x95\x81\x06%'           # 100.801
            b'?\xe9\xa1\xca\xc0\x83\x12o'  # 0.801
            b'@Y\x0c\xdd/\x1a\x9f\xbe'     # 100.201
            b'?\xc9\xba^5?|\xee'           # 0.201

        )
        self.assertEqual(expected, wkb.dumps(poly))

    def test_3d(self):
        poly = dict(type='Polygon', coordinates=[
            [[100.001, 0.001, 0.0], [101.12345, 0.001, 1.0],
             [101.001, 1.001, 2.0],
             [100.001, 0.001, 0.0]],
            [[100.201, 0.201, 0.0], [100.801, 0.201, 1.0],
             [100.801, 0.801, 2.0], [100.201, 0.201, 0.0]],
        ])
        expected = (
            b'\x00'
            b'\x00\x00\x10\x03'  # type
            # number of rings, 4 byte int
            b'\x00\x00\x00\x02'
            # number of verts in ring (4)
            b'\x00\x00\x00\x04'
            # coords
            b'@Y\x00\x10bM\xd2\xf2'              # 100.001
            b'?PbM\xd2\xf1\xa9\xfc'              # 0.001
            b'\x00\x00\x00\x00\x00\x00\x00\x00'  # 0.0
            b'@YG\xe6\x9a\xd4,='                 # 101.12345
            b'?PbM\xd2\xf1\xa9\xfc'              # 0.001
            b'?\xf0\x00\x00\x00\x00\x00\x00'     # 1.0
            b'@Y@\x10bM\xd2\xf2'                 # 101.001
            b'?\xf0\x04\x18\x93t\xbcj'           # 1.001
            b'@\x00\x00\x00\x00\x00\x00\x00'     # 2.0
            b'@Y\x00\x10bM\xd2\xf2'              # 100.001
            b'?PbM\xd2\xf1\xa9\xfc'              # 0.001
            b'\x00\x00\x00\x00\x00\x00\x00\x00'  # 0.0
            # number of verts in ring (4)
            b'\x00\x00\x00\x04'
            # coords
            b'@Y\x0c\xdd/\x1a\x9f\xbe'           # 100.201
            b'?\xc9\xba^5?|\xee'                 # 0.201
            b'\x00\x00\x00\x00\x00\x00\x00\x00'  # 0.0
            b'@Y3C\x95\x81\x06%'                 # 100.801
            b'?\xc9\xba^5?|\xee'                 # 0.201
            b'?\xf0\x00\x00\x00\x00\x00\x00'     # 1.0
            b'@Y3C\x95\x81\x06%'                 # 100.801
            b'?\xe9\xa1\xca\xc0\x83\x12o'        # 0.801
            b'@\x00\x00\x00\x00\x00\x00\x00'     # 2.0
            b'@Y\x0c\xdd/\x1a\x9f\xbe'           # 100.201
            b'?\xc9\xba^5?|\xee'                 # 0.201
            b'\x00\x00\x00\x00\x00\x00\x00\x00'  # 0.0
        )
        self.assertEqual(expected, wkb.dumps(poly))

    def test_4d(self):
        poly = dict(type='Polygon', coordinates=[
            [[100.001, 0.001, 0.0, 0.0], [101.12345, 0.001, 1.0, 1.0],
             [101.001, 1.001, 2.0, 2.0],
             [100.001, 0.001, 0.0, 0.0]],
            [[100.201, 0.201, 0.0, 0.0], [100.801, 0.201, 1.0, 0.0],
             [100.801, 0.801, 2.0, 1.0], [100.201, 0.201, 0.0, 0.0]],
        ])
        expected = (
            b'\x00'
            b'\x00\x00\x30\x03'  # type
            # number of rings, 4 byte int
            b'\x00\x00\x00\x02'
            # number of verts in ring (4)
            b'\x00\x00\x00\x04'
            # coords
            b'@Y\x00\x10bM\xd2\xf2'              # 100.001
            b'?PbM\xd2\xf1\xa9\xfc'              # 0.001
            b'\x00\x00\x00\x00\x00\x00\x00\x00'  # 0.0
            b'\x00\x00\x00\x00\x00\x00\x00\x00'  # 0.0
            b'@YG\xe6\x9a\xd4,='                 # 101.12345
            b'?PbM\xd2\xf1\xa9\xfc'              # 0.001
            b'?\xf0\x00\x00\x00\x00\x00\x00'     # 1.0
            b'?\xf0\x00\x00\x00\x00\x00\x00'     # 1.0
            b'@Y@\x10bM\xd2\xf2'                 # 101.001
            b'?\xf0\x04\x18\x93t\xbcj'           # 1.001
            b'@\x00\x00\x00\x00\x00\x00\x00'     # 2.0
            b'@\x00\x00\x00\x00\x00\x00\x00'     # 2.0
            b'@Y\x00\x10bM\xd2\xf2'              # 100.001
            b'?PbM\xd2\xf1\xa9\xfc'              # 0.001
            b'\x00\x00\x00\x00\x00\x00\x00\x00'  # 0.0
            b'\x00\x00\x00\x00\x00\x00\x00\x00'  # 0.0
            # number of verts in ring (4)
            b'\x00\x00\x00\x04'
            # coords
            b'@Y\x0c\xdd/\x1a\x9f\xbe'           # 100.201
            b'?\xc9\xba^5?|\xee'                 # 0.201
            b'\x00\x00\x00\x00\x00\x00\x00\x00'  # 0.0
            b'\x00\x00\x00\x00\x00\x00\x00\x00'  # 0.0
            b'@Y3C\x95\x81\x06%'                 # 100.801
            b'?\xc9\xba^5?|\xee'                 # 0.201
            b'?\xf0\x00\x00\x00\x00\x00\x00'     # 1.0
            b'\x00\x00\x00\x00\x00\x00\x00\x00'  # 0.0
            b'@Y3C\x95\x81\x06%'                 # 100.801
            b'?\xe9\xa1\xca\xc0\x83\x12o'        # 0.801
            b'@\x00\x00\x00\x00\x00\x00\x00'     # 2.0
            b'?\xf0\x00\x00\x00\x00\x00\x00'     # 1.0
            b'@Y\x0c\xdd/\x1a\x9f\xbe'           # 100.201
            b'?\xc9\xba^5?|\xee'                 # 0.201
            b'\x00\x00\x00\x00\x00\x00\x00\x00'  # 0.0
            b'\x00\x00\x00\x00\x00\x00\x00\x00'  # 0.0
        )
        self.assertEqual(expected, wkb.dumps(poly))


class MultiPointDumpsTestCase(unittest.TestCase):

    def test_2d(self):
        mp = dict(type='MultiPoint', coordinates=[
            [2.2, 4.4], [10.0, 3.1], [5.1, 20.0],
        ])
        expected = (
            b'\x01'  # little endian
            b'\x04\x00\x00\x00'
            # number of points: 3
            b'\x03\x00\x00\x00'
            # point 2d
            b'\x01\x00\x00\x00'
            b'\x9a\x99\x99\x99\x99\x99\x01@'  # 2.2
            b'\x9a\x99\x99\x99\x99\x99\x11@'  # 4.4
            # point 2d
            b'\x01\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00$@'     # 10.0
            b'\xcd\xcc\xcc\xcc\xcc\xcc\x08@'  # 3.1
            # point 2d
            b'\x01\x00\x00\x00'
            b'ffffff\x14@'                    # 5.1
            b'\x00\x00\x00\x00\x00\x004@'     # 20.0
        )
        self.assertEqual(expected, wkb.dumps(mp, big_endian=False))
