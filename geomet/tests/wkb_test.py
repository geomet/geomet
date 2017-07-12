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
import unittest

from geomet import wkb


class WKBTestCase(unittest.TestCase):

    def test_unsupported_geom_type(self):
        geom = dict(type='Tetrahedron', coordinates=[])
        with self.assertRaises(ValueError) as ar:
            wkb.dumps(geom)
        self.assertEqual("Unsupported geometry type 'Tetrahedron'",
                         str(ar.exception))

    def test_empty(self):
        types = [
            'Point',
            'LineString',
            'Polygon',
            'MultiPoint',
            'MultiLineString',
            'MultiPolygon',
        ]
        coords = [
            [],
            [[]],
            [[[]]],
            [[]],
            [[[]]],
            [[[[]]]],
        ]
        for t, c in zip(types, coords):
            geom = dict(type=t, coordinates=c)
            with self.assertRaises(ValueError):
                wkb.dumps(geom)

        gc = dict(type='GeometryCollection', geometries=[])
        with self.assertRaises(ValueError):
            wkb.dumps(gc)


class PointTestCase(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.pt2d = dict(type='Point', coordinates=[0.0, 1.0])
        self.pt2d_wkb = (
            b'\x01'  # little endian
            b'\x01\x00\x00\x00'  # type
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\xf0?'
        )
        self.pt3d = dict(type='Point', coordinates=[0.0, 1.0, 2.0])
        self.pt3d_wkb = (
            b'\x00'  # big endian
            b'\x00\x00\x03\xe9'  # type
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'?\xf0\x00\x00\x00\x00\x00\x00'
            b'@\x00\x00\x00\x00\x00\x00\x00'
        )
        self.pt4d = dict(type='Point', coordinates=[0.0, 1.0, 2.0, 4.0])
        self.pt4d_wkb = (
            b'\x01'  # little endian
            b'\xb9\x0b\x00\x00'  # type
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\xf0?'
            b'\x00\x00\x00\x00\x00\x00\x00@'
            b'\x00\x00\x00\x00\x00\x00\x10@'
        )

        self.pt2d_srid4326 = dict(
            type='Point',
            coordinates=[0.0, 1.0],
            meta=dict(srid=4326),
            crs={'properties': {'name': 'EPSG4326'}, 'type': 'name'},
        )
        self.pt2d_srid4326_wkb = (
            b'\x01'  # little endian
            b'\x01\x00\x00\x20'  # type, with SRID flag set (0x20)
            b'\xe6\x10\x00\x00'  # 4 bytes containing SRID (SRID=4326)
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\xf0?'
        )

    def test_dumps_2d(self):
        self.assertEqual(self.pt2d_wkb, wkb.dumps(self.pt2d, big_endian=False))

    def test_dumps_3d(self):
        self.assertEqual(self.pt3d_wkb, wkb.dumps(self.pt3d))

    def test_dumps_4d(self):
        self.assertEqual(self.pt4d_wkb, wkb.dumps(self.pt4d, big_endian=False))

    def test_dumps_2d_srid4326(self):
        self.assertEqual(
            self.pt2d_srid4326_wkb,
            wkb.dumps(self.pt2d_srid4326, big_endian=False),
        )

    def test_loads_2d(self):
        self.assertEqual(self.pt2d, wkb.loads(self.pt2d_wkb))

    def test_loads_z(self):
        self.assertEqual(self.pt3d, wkb.loads(self.pt3d_wkb))

    def test_loads_m(self):
        exp_pt = self.pt3d.copy()
        exp_pt['coordinates'].insert(2, 0.0)

        pt_wkb = b'\x00\x00\x00\x07\xd1'
        pt_wkb += self.pt3d_wkb[5:]
        self.assertEqual(exp_pt, wkb.loads(pt_wkb))

    def test_loads_zm(self):
        self.assertEqual(self.pt4d, wkb.loads(self.pt4d_wkb))

    def test_loads_2d_srid4326(self):
        self.assertEqual(self.pt2d_srid4326, wkb.loads(self.pt2d_srid4326_wkb))


class LineStringTestCase(unittest.TestCase):

    def setUp(self):
        self.ls2d = dict(type='LineString', coordinates=[[2.2, 4.4],
                                                         [3.1, 5.1]])
        self.ls2d_wkb = (
            b'\x00'  # big endian
            b'\x00\x00\x00\x02'  # type
            b'\x00\x00\x00\x02'  # 2 vertices
            b'@\x01\x99\x99\x99\x99\x99\x9a'  # 2.2
            b'@\x11\x99\x99\x99\x99\x99\x9a'  # 4.4
            b'@\x08\xcc\xcc\xcc\xcc\xcc\xcd'  # 3.1
            b'@\x14ffffff'                    # 5.1
        )
        self.ls3d = dict(type='LineString', coordinates=[[2.2, 4.4, 10.0],
                                                         [3.1, 5.1, 20.0]])
        self.ls3d_wkb = (
            b'\x01'  # little endian
            b'\xea\x03\x00\x00'  # type
            b'\x02\x00\x00\x00'  # 2 vertices
            b'\x9a\x99\x99\x99\x99\x99\x01@'  # 2.2
            b'\x9a\x99\x99\x99\x99\x99\x11@'  # 4.4
            b'\x00\x00\x00\x00\x00\x00$@'     # 10.0
            b'\xcd\xcc\xcc\xcc\xcc\xcc\x08@'  # 3.1
            b'ffffff\x14@'                    # 5.1
            b'\x00\x00\x00\x00\x00\x004@'     # 20.0
        )
        self.ls4d = dict(type='LineString',
                         coordinates=[[2.2, -4.4, -10.0, 0.1],
                                      [-3.1, 5.1, 20.0, -0.9]])
        self.ls4d_wkb = (
            b'\x00'  # big endian
            b'\x00\x00\x0b\xba'  # type
            b'\x00\x00\x00\x02'  # 2 vertices
            b'@\x01\x99\x99\x99\x99\x99\x9a'     # 2.2
            b'\xc0\x11\x99\x99\x99\x99\x99\x9a'  # -4.4
            b'\xc0$\x00\x00\x00\x00\x00\x00'     # -10.0
            b'?\xb9\x99\x99\x99\x99\x99\x9a'     # 0.1
            b'\xc0\x08\xcc\xcc\xcc\xcc\xcc\xcd'  # -3.1
            b'@\x14ffffff'                       # 5.1
            b'@4\x00\x00\x00\x00\x00\x00'        # 20.0
            b'\xbf\xec\xcc\xcc\xcc\xcc\xcc\xcd'  # -0.9
        )

        self.ls2d_srid1234 = dict(
            type='LineString',
            coordinates=[[2.2, 4.4], [3.1, 5.1]],
            meta=dict(srid=1234),
            crs={'properties': {'name': 'EPSG1234'}, 'type': 'name'},
        )
        self.ls2d_srid1234_wkb = (
            b'\x00'  # big endian
            b'\x20\x00\x00\x02'  # type with SRID flag set
            b'\x00\x00\x04\xd2'  # srid
            b'\x00\x00\x00\x02'  # 2 vertices
            b'@\x01\x99\x99\x99\x99\x99\x9a'  # 2.2
            b'@\x11\x99\x99\x99\x99\x99\x9a'  # 4.4
            b'@\x08\xcc\xcc\xcc\xcc\xcc\xcd'  # 3.1
            b'@\x14ffffff'                    # 5.1
        )

    def test_dumps_2d(self):
        self.assertEqual(self.ls2d_wkb, wkb.dumps(self.ls2d))

    def test_dumps_3d(self):
        self.assertEqual(self.ls3d_wkb, wkb.dumps(self.ls3d, big_endian=False))

    def test_dumps_4d(self):
        self.assertEqual(self.ls4d_wkb, wkb.dumps(self.ls4d))

    def test_dumps_2d_srid1234(self):
        self.assertEqual(self.ls2d_srid1234_wkb, wkb.dumps(self.ls2d_srid1234))

    def test_loads_2d(self):
        self.assertEqual(self.ls2d, wkb.loads(self.ls2d_wkb))

    def test_loads_z(self):
        self.assertEqual(self.ls3d, wkb.loads(self.ls3d_wkb))

    def test_loads_m(self):
        exp_ls = self.ls3d.copy()
        for vert in exp_ls['coordinates']:
            vert.insert(2, 0.0)

        ls_wkb = b'\x01\xd2\x07\x00\x00'
        ls_wkb += self.ls3d_wkb[5:]
        self.assertEqual(exp_ls, wkb.loads(ls_wkb))

    def test_loads_zm(self):
        self.assertEqual(self.ls4d, wkb.loads(self.ls4d_wkb))

    def test_loads_2d_srid1234(self):
        self.assertEqual(self.ls2d_srid1234, wkb.loads(self.ls2d_srid1234_wkb))


class PolygonTestCase(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.poly2d = dict(type='Polygon', coordinates=[
            [[100.001, 0.001], [101.12345, 0.001], [101.001, 1.001],
             [100.001, 0.001]],
            [[100.201, 0.201], [100.801, 0.201], [100.801, 0.801],
             [100.201, 0.201]],
        ])
        self.poly2d_wkb = (
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
        self.poly3d = dict(type='Polygon', coordinates=[
            [[100.001, 0.001, 0.0], [101.12345, 0.001, 1.0],
             [101.001, 1.001, 2.0],
             [100.001, 0.001, 0.0]],
            [[100.201, 0.201, 0.0], [100.801, 0.201, 1.0],
             [100.801, 0.801, 2.0], [100.201, 0.201, 0.0]],
        ])
        self.poly3d_wkb = (
            b'\x00'
            b'\x00\x00\x03\xeb'  # type
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
        self.poly4d = dict(type='Polygon', coordinates=[
            [[100.001, 0.001, 0.0, 0.0], [101.12345, 0.001, 1.0, 1.0],
             [101.001, 1.001, 2.0, 2.0],
             [100.001, 0.001, 0.0, 0.0]],
            [[100.201, 0.201, 0.0, 0.0], [100.801, 0.201, 1.0, 0.0],
             [100.801, 0.801, 2.0, 1.0], [100.201, 0.201, 0.0, 0.0]],
        ])
        self.poly4d_wkb = (
            b'\x00'
            b'\x00\x00\x0b\xbb'  # type
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

        self.poly2d_srid26918 = dict(
            type='Polygon',
            coordinates=[
                [[100.001, 0.001], [101.12345, 0.001], [101.001, 1.001],
                 [100.001, 0.001]],
                [[100.201, 0.201], [100.801, 0.201], [100.801, 0.801],
                 [100.201, 0.201]],
            ],
            meta=dict(srid=26918),
            crs={'properties': {'name': 'EPSG26918'}, 'type': 'name'},
        )

        self.poly2d_srid26918_wkb = (
            b'\x00'  # big endian
            b'\x20\x00\x00\x03'  # type, with SRID flag set (0x20)
            b'\x00\x00\x69\x26'  # 4 bytes containing SRID (SRID=26918)
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

    def test_dumps_2d(self):
        self.assertEqual(self.poly2d_wkb, wkb.dumps(self.poly2d))

    def test_dumps_3d(self):
        self.assertEqual(self.poly3d_wkb, wkb.dumps(self.poly3d))

    def test_dumps_4d(self):
        self.assertEqual(self.poly4d_wkb, wkb.dumps(self.poly4d))

    def test_dumps_2d_srid26918(self):
        self.assertEqual(
            self.poly2d_srid26918_wkb, wkb.dumps(self.poly2d_srid26918)
        )

    def test_loads_2d(self):
        self.assertEqual(self.poly2d, wkb.loads(self.poly2d_wkb))

    def test_loads_z(self):
        self.assertEqual(self.poly3d, wkb.loads(self.poly3d_wkb))

    def test_loads_m(self):
        exp_poly = self.poly3d.copy()
        for ring in exp_poly['coordinates']:
            for vert in ring:
                vert.insert(2, 0.0)

        poly_wkb = b'\x00\x00\x00\x07\xd3'
        poly_wkb += self.poly3d_wkb[5:]
        poly_wkb = bytes(poly_wkb)
        self.assertEqual(exp_poly, wkb.loads(poly_wkb))

    def test_loads_zm(self):
        self.assertEqual(self.poly4d, wkb.loads(self.poly4d_wkb))

    def test_loads_2d_srid26918(self):
        self.assertEqual(
            self.poly2d_srid26918, wkb.loads(self.poly2d_srid26918_wkb)
        )


class MultiPointTestCase(unittest.TestCase):

    def setUp(self):
        self.multipoint2d = dict(type='MultiPoint', coordinates=[
            [2.2, 4.4], [10.0, 3.1], [5.1, 20.0],
        ])
        self.multipoint2d_wkb = (
            b'\x01'  # little endian
            b'\x04\x00\x00\x00'
            # number of points: 3
            b'\x03\x00\x00\x00'
            # point 2d
            b'\x01'  # little endian
            b'\x01\x00\x00\x00'
            b'\x9a\x99\x99\x99\x99\x99\x01@'  # 2.2
            b'\x9a\x99\x99\x99\x99\x99\x11@'  # 4.4
            # point 2d
            b'\x01'  # little endian
            b'\x01\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00$@'     # 10.0
            b'\xcd\xcc\xcc\xcc\xcc\xcc\x08@'  # 3.1
            # point 2d
            b'\x01'  # little endian
            b'\x01\x00\x00\x00'
            b'ffffff\x14@'                    # 5.1
            b'\x00\x00\x00\x00\x00\x004@'     # 20.0
        )
        self.multipoint3d = dict(type='MultiPoint', coordinates=[
            [2.2, 4.4, 3.0], [10.0, 3.1, 2.0], [5.1, 20.0, 4.4],
        ])
        self.multipoint3d_wkb = (
            b'\x01'  # little endian
            b'\xec\x03\x00\x00'
            # number of points: 3
            b'\x03\x00\x00\x00'
            # point 3d
            b'\x01'  # little endian
            b'\xe9\x03\x00\x00'
            b'\x9a\x99\x99\x99\x99\x99\x01@'  # 2.2
            b'\x9a\x99\x99\x99\x99\x99\x11@'  # 4.4
            b'\x00\x00\x00\x00\x00\x00\x08@'  # 3.0
            # point 3d
            b'\x01'  # little endian
            b'\xe9\x03\x00\x00'
            b'\x00\x00\x00\x00\x00\x00$@'     # 10.0
            b'\xcd\xcc\xcc\xcc\xcc\xcc\x08@'  # 3.1
            b'\x00\x00\x00\x00\x00\x00\x00@'  # 2.0
            # point 3d
            b'\x01'  # little endian
            b'\xe9\x03\x00\x00'
            b'ffffff\x14@'                    # 5.1
            b'\x00\x00\x00\x00\x00\x004@'     # 20.0
            b'\x9a\x99\x99\x99\x99\x99\x11@'  # 4.4
        )
        self.multipoint4d = dict(type='MultiPoint', coordinates=[
            [2.2, 4.4, 0.0, 3.0], [10.0, 3.1, 0.0, 2.0], [5.1, 20.0, 0.0, 4.4],
        ])
        self.multipoint4d_wkb = (
            b'\x01'  # little endian
            b'\xbc\x0b\x00\x00'
            # number of points: 3
            b'\x03\x00\x00\x00'
            # point 4d
            b'\x01'  # little endian
            b'\xb9\x0b\x00\x00'
            b'\x9a\x99\x99\x99\x99\x99\x01@'     # 2.2
            b'\x9a\x99\x99\x99\x99\x99\x11@'     # 4.4
            b'\x00\x00\x00\x00\x00\x00\x00\x00'  # 0.0
            b'\x00\x00\x00\x00\x00\x00\x08@'     # 3.0
            # point 4d
            b'\x01'  # little endian
            b'\xb9\x0b\x00\x00'
            b'\x00\x00\x00\x00\x00\x00$@'        # 10.0
            b'\xcd\xcc\xcc\xcc\xcc\xcc\x08@'     # 3.1
            b'\x00\x00\x00\x00\x00\x00\x00\x00'  # 0.0
            b'\x00\x00\x00\x00\x00\x00\x00@'     # 2.0
            # point 4d
            b'\x01'  # little endian
            b'\xb9\x0b\x00\x00'
            b'ffffff\x14@'                       # 5.1
            b'\x00\x00\x00\x00\x00\x004@'        # 20.0
            b'\x00\x00\x00\x00\x00\x00\x00\x00'  # 0.0
            b'\x9a\x99\x99\x99\x99\x99\x11@'     # 4.4
        )
        self.multipoint2d_srid664 = dict(
            type='MultiPoint',
            coordinates=[[2.2, 4.4], [10.0, 3.1], [5.1, 20.0]],
            meta=dict(srid=664),
            crs={'properties': {'name': 'EPSG664'}, 'type': 'name'},
        )
        self.multipoint2d_srid664_wkb = (
            b'\x01'  # little endian
            b'\x04\x00\x00\x20'  # type with SRID flag set
            b'\x98\x02\x00\x00'  # SRID 664
            # number of points: 3
            b'\x03\x00\x00\x00'
            # point 2d
            b'\x01'  # little endian
            b'\x01\x00\x00\x00'
            b'\x9a\x99\x99\x99\x99\x99\x01@'  # 2.2
            b'\x9a\x99\x99\x99\x99\x99\x11@'  # 4.4
            # point 2d
            b'\x01'  # little endian
            b'\x01\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00$@'     # 10.0
            b'\xcd\xcc\xcc\xcc\xcc\xcc\x08@'  # 3.1
            # point 2d
            b'\x01'  # little endian
            b'\x01\x00\x00\x00'
            b'ffffff\x14@'                    # 5.1
            b'\x00\x00\x00\x00\x00\x004@'     # 20.0
        )

    def test_dumps_2d(self):
        self.assertEqual(
            self.multipoint2d_wkb,
            wkb.dumps(self.multipoint2d, big_endian=False)
        )

    def test_dumps_3d(self):
        self.assertEqual(
            self.multipoint3d_wkb,
            wkb.dumps(self.multipoint3d, big_endian=False)
        )

    def test_dumps_4d(self):
        self.assertEqual(
            self.multipoint4d_wkb,
            wkb.dumps(self.multipoint4d, big_endian=False)
        )

    def test_dumps_2d_srid664(self):
        self.assertEqual(
            self.multipoint2d_srid664_wkb,
            wkb.dumps(self.multipoint2d_srid664, big_endian=False),
        )

    def test_loads_2d(self):
        self.assertEqual(self.multipoint2d, wkb.loads(self.multipoint2d_wkb))

    def test_loads_z(self):
        self.assertEqual(self.multipoint3d, wkb.loads(self.multipoint3d_wkb))

    def test_loads_m(self):
        exp_mp = self.multipoint3d.copy()
        for pt in exp_mp['coordinates']:
            pt.insert(2, 0.0)

        mp_wkb = (
            b'\x01'  # little endian
            b'\xd4\x07\x00\x00'
            # number of points: 3
            b'\x03\x00\x00\x00'
            # point 3d
            b'\x01'  # little endian
            b'\xd1\x07\x00\x00'
            b'\x9a\x99\x99\x99\x99\x99\x01@'  # 2.2
            b'\x9a\x99\x99\x99\x99\x99\x11@'  # 4.4
            b'\x00\x00\x00\x00\x00\x00\x08@'  # 3.0
            # point 3d
            b'\x01'  # little endian
            b'\xd1\x07\x00\x00'
            b'\x00\x00\x00\x00\x00\x00$@'     # 10.0
            b'\xcd\xcc\xcc\xcc\xcc\xcc\x08@'  # 3.1
            b'\x00\x00\x00\x00\x00\x00\x00@'  # 2.0
            # point 3d
            b'\x01'  # little endian
            b'\xd1\x07\x00\x00'
            b'ffffff\x14@'                    # 5.1
            b'\x00\x00\x00\x00\x00\x004@'     # 20.0
            b'\x9a\x99\x99\x99\x99\x99\x11@'  # 4.4
        )

        self.assertEqual(exp_mp, wkb.loads(mp_wkb))

    def test_loads_zm(self):
        self.assertEqual(self.multipoint4d, wkb.loads(self.multipoint4d_wkb))

    def test_loads_2d_srid664(self):
        self.assertEqual(
            wkb.loads(self.multipoint2d_srid664_wkb),
            self.multipoint2d_srid664,
        )


class MultiLineStringTestCase(unittest.TestCase):

    def setUp(self):
        self.mls2d = dict(type='MultiLineString', coordinates=[
            [[2.2, 4.4], [3.1, 5.1], [5.1, 20.0]],
            [[20.0, 2.2], [3.1, 4.4]],
        ])
        self.mls2d_wkb = (
            b'\x00'
            b'\x00\x00\x00\x05'
            b'\x00\x00\x00\x02'  # number of linestrings
            b'\x00'
            b'\x00\x00\x00\x02'
            b'\x00\x00\x00\x03'
            b'@\x01\x99\x99\x99\x99\x99\x9a'  # 2.2
            b'@\x11\x99\x99\x99\x99\x99\x9a'  # 4.4
            b'@\x08\xcc\xcc\xcc\xcc\xcc\xcd'  # 3.1
            b'@\x14ffffff'                    # 5.1
            b'@\x14ffffff'                    # 5.1
            b'@4\x00\x00\x00\x00\x00\x00'     # 20.0
            b'\x00'
            b'\x00\x00\x00\x02'
            b'\x00\x00\x00\x02'
            b'@4\x00\x00\x00\x00\x00\x00'     # 20.0
            b'@\x01\x99\x99\x99\x99\x99\x9a'  # 2.2
            b'@\x08\xcc\xcc\xcc\xcc\xcc\xcd'  # 3.1
            b'@\x11\x99\x99\x99\x99\x99\x9a'  # 4.4
        )
        self.mls3d = dict(type='MultiLineString', coordinates=[
            [[2.2, 0.0, 4.4], [3.1, 5.1, 5.1], [5.1, 20.0, 0.0]],
            [[20.0, 2.2, 2.2], [0.0, 3.1, 4.4]],
        ])
        self.mls3d_wkb = (
            b'\x00'
            b'\x00\x00\x03\xed'
            b'\x00\x00\x00\x02'  # number of linestrings
            b'\x00'
            b'\x00\x00\x03\xea'
            b'\x00\x00\x00\x03'
            b'@\x01\x99\x99\x99\x99\x99\x9a'  # 2.2
            b'\x00\x00\x00\x00\x00\x00\x00\x00'  # 0.0
            b'@\x11\x99\x99\x99\x99\x99\x9a'  # 4.4
            b'@\x08\xcc\xcc\xcc\xcc\xcc\xcd'  # 3.1
            b'@\x14ffffff'                    # 5.1
            b'@\x14ffffff'                    # 5.1
            b'@\x14ffffff'                    # 5.1
            b'@4\x00\x00\x00\x00\x00\x00'     # 20.0
            b'\x00\x00\x00\x00\x00\x00\x00\x00'  # 0.0
            b'\x00'
            b'\x00\x00\x03\xea'
            b'\x00\x00\x00\x02'
            b'@4\x00\x00\x00\x00\x00\x00'     # 20.0
            b'@\x01\x99\x99\x99\x99\x99\x9a'  # 2.2
            b'@\x01\x99\x99\x99\x99\x99\x9a'  # 2.2
            b'\x00\x00\x00\x00\x00\x00\x00\x00'  # 0.0
            b'@\x08\xcc\xcc\xcc\xcc\xcc\xcd'  # 3.1
            b'@\x11\x99\x99\x99\x99\x99\x9a'  # 4.4
        )
        self.mls4d = dict(type='MultiLineString', coordinates=[
            [[2.2, 4.4, 0.0, 3.0], [10.0, 0.0, 3.1, 2.0]],
            [[0.0, 5.1, 20.0, 4.4]],
        ])
        self.mls4d_wkb = (
            b'\x01'
            b'\xbd\x0b\x00\x00'
            b'\x02\x00\x00\x00'  # two linestrings
            b'\x01'
            b'\xba\x0b\x00\x00'
            b'\x02\x00\x00\x00'  # two points
            b'\x9a\x99\x99\x99\x99\x99\x01@'     # 2.2
            b'\x9a\x99\x99\x99\x99\x99\x11@'     # 4.4
            b'\x00\x00\x00\x00\x00\x00\x00\x00'  # 0.0
            b'\x00\x00\x00\x00\x00\x00\x08@'     # 3.0
            b'\x00\x00\x00\x00\x00\x00$@'        # 10.0
            b'\x00\x00\x00\x00\x00\x00\x00\x00'  # 0.0
            b'\xcd\xcc\xcc\xcc\xcc\xcc\x08@'     # 3.1
            b'\x00\x00\x00\x00\x00\x00\x00@'     # 2.0
            b'\x01'
            b'\xba\x0b\x00\x00'
            b'\x01\x00\x00\x00'  # one point
            b'\x00\x00\x00\x00\x00\x00\x00\x00'  # 0.0
            b'ffffff\x14@'                       # 5.1
            b'\x00\x00\x00\x00\x00\x004@'        # 20.0
            b'\x9a\x99\x99\x99\x99\x99\x11@'     # 4.4
        )

        self.mls2d_srid4326 = dict(
            type='MultiLineString',
            coordinates=[[[2.2, 4.4], [3.1, 5.1], [5.1, 20.0]],
                         [[20.0, 2.2], [3.1, 4.4]]],
            meta=dict(srid=4326),
            crs={'properties': {'name': 'EPSG4326'}, 'type': 'name'},
        )
        self.mls2d_srid4326_wkb = (
            b'\x00'
            b'\x20\x00\x00\x05'  # type with SRID flag set
            b'\x00\x00\x10\xe6'  # SRID 4326
            b'\x00\x00\x00\x02'  # number of linestrings
            b'\x00'
            b'\x00\x00\x00\x02'
            b'\x00\x00\x00\x03'
            b'@\x01\x99\x99\x99\x99\x99\x9a'  # 2.2
            b'@\x11\x99\x99\x99\x99\x99\x9a'  # 4.4
            b'@\x08\xcc\xcc\xcc\xcc\xcc\xcd'  # 3.1
            b'@\x14ffffff'                    # 5.1
            b'@\x14ffffff'                    # 5.1
            b'@4\x00\x00\x00\x00\x00\x00'     # 20.0
            b'\x00'
            b'\x00\x00\x00\x02'
            b'\x00\x00\x00\x02'
            b'@4\x00\x00\x00\x00\x00\x00'     # 20.0
            b'@\x01\x99\x99\x99\x99\x99\x9a'  # 2.2
            b'@\x08\xcc\xcc\xcc\xcc\xcc\xcd'  # 3.1
            b'@\x11\x99\x99\x99\x99\x99\x9a'  # 4.4
        )

    def test_dumps_2d(self):
        self.assertEqual(self.mls2d_wkb, wkb.dumps(self.mls2d))

    def test_dumps_3d(self):
        self.assertEqual(self.mls3d_wkb, wkb.dumps(self.mls3d))

    def test_dumps_4d(self):
        self.assertEqual(self.mls4d_wkb,
                         wkb.dumps(self.mls4d, big_endian=False))

    def test_dumps_2d_srid4326(self):
        self.assertEqual(
            self.mls2d_srid4326_wkb, wkb.dumps(self.mls2d_srid4326)
        )

    def test_loads_2d(self):
        self.assertEqual(self.mls2d, wkb.loads(self.mls2d_wkb))

    def test_loads_z(self):
        self.assertEqual(self.mls3d, wkb.loads(self.mls3d_wkb))

    def test_loads_m(self):
        exp_mls = self.mls3d.copy()
        for ls in exp_mls['coordinates']:
            for vert in ls:
                vert.insert(2, 0.0)

        mls_wkb = (
            b'\x00'
            b'\x00\x00\x07\xd5'
            b'\x00\x00\x00\x02'  # number of linestrings
            b'\x00'
            b'\x00\x00\x07\xd2'
            b'\x00\x00\x00\x03'
            b'@\x01\x99\x99\x99\x99\x99\x9a'  # 2.2
            b'\x00\x00\x00\x00\x00\x00\x00\x00'  # 0.0
            b'@\x11\x99\x99\x99\x99\x99\x9a'  # 4.4
            b'@\x08\xcc\xcc\xcc\xcc\xcc\xcd'  # 3.1
            b'@\x14ffffff'                    # 5.1
            b'@\x14ffffff'                    # 5.1
            b'@\x14ffffff'                    # 5.1
            b'@4\x00\x00\x00\x00\x00\x00'     # 20.0
            b'\x00\x00\x00\x00\x00\x00\x00\x00'  # 0.0
            b'\x00'
            b'\x00\x00\x07\xd2'
            b'\x00\x00\x00\x02'
            b'@4\x00\x00\x00\x00\x00\x00'     # 20.0
            b'@\x01\x99\x99\x99\x99\x99\x9a'  # 2.2
            b'@\x01\x99\x99\x99\x99\x99\x9a'  # 2.2
            b'\x00\x00\x00\x00\x00\x00\x00\x00'  # 0.0
            b'@\x08\xcc\xcc\xcc\xcc\xcc\xcd'  # 3.1
            b'@\x11\x99\x99\x99\x99\x99\x9a'  # 4.4
        )
        self.assertEqual(exp_mls, wkb.loads(mls_wkb))

    def test_loads_zm(self):
        self.assertEqual(self.mls4d, wkb.loads(self.mls4d_wkb))

    def test_loads_2d_srid4326(self):
        self.assertEqual(
            self.mls2d_srid4326, wkb.loads(self.mls2d_srid4326_wkb)
        )


class MultiPolygonTestCase(unittest.TestCase):

    def setUp(self):
        self.mpoly2d = dict(type='MultiPolygon', coordinates=[
            [[[102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0],
              [102.0, 2.0]]],
            [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0],
              [100.0, 0.0]],
             [[100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8],
              [100.2, 0.2]]],
        ])
        self.mpoly2d_wkb = (
            b'\x01'  # little endian
            b'\x06\x00\x00\x00'  # 2d multipolygon
            b'\x02\x00\x00\x00'  # two polygons
            b'\x01'  # little endian
            b'\x03\x00\x00\x00'  # 2d polygon
            b'\x01\x00\x00\x00'  # 1 ring
            b'\x05\x00\x00\x00'  # 5 vertices
            b'\x00\x00\x00\x00\x00\x80Y@'
            b'\x00\x00\x00\x00\x00\x00\x00@'
            b'\x00\x00\x00\x00\x00\xc0Y@'
            b'\x00\x00\x00\x00\x00\x00\x00@'
            b'\x00\x00\x00\x00\x00\xc0Y@'
            b'\x00\x00\x00\x00\x00\x00\x08@'
            b'\x00\x00\x00\x00\x00\x80Y@'
            b'\x00\x00\x00\x00\x00\x00\x08@'
            b'\x00\x00\x00\x00\x00\x80Y@'
            b'\x00\x00\x00\x00\x00\x00\x00@'
            b'\x01'  # little endian
            b'\x03\x00\x00\x00'  # 2d polygon
            b'\x02\x00\x00\x00'  # 2 rings
            b'\x05\x00\x00\x00'  # first ring, 5 vertices
            b'\x00\x00\x00\x00\x00\x00Y@'
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00@Y@'
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00@Y@'
            b'\x00\x00\x00\x00\x00\x00\xf0?'
            b'\x00\x00\x00\x00\x00\x00Y@'
            b'\x00\x00\x00\x00\x00\x00\xf0?'
            b'\x00\x00\x00\x00\x00\x00Y@'
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x05\x00\x00\x00'  # second ring, 5 vertices
            b'\xcd\xcc\xcc\xcc\xcc\x0cY@'
            b'\x9a\x99\x99\x99\x99\x99\xc9?'
            b'333333Y@'
            b'\x9a\x99\x99\x99\x99\x99\xc9?'
            b'333333Y@'
            b'\x9a\x99\x99\x99\x99\x99\xe9?'
            b'\xcd\xcc\xcc\xcc\xcc\x0cY@'
            b'\x9a\x99\x99\x99\x99\x99\xe9?'
            b'\xcd\xcc\xcc\xcc\xcc\x0cY@'
            b'\x9a\x99\x99\x99\x99\x99\xc9?'
        )
        self.mpoly3d = dict(type='MultiPolygon', coordinates=[
            [[[102.0, 2.0, 0.0], [103.0, 2.0, 1.0], [103.0, 3.0, 2.0],
              [102.0, 3.0, 3.0], [102.0, 2.0, 4.0]]],
            [[[100.0, 0.0, 5.0], [101.0, 0.0, 6.0], [101.0, 1.0, 7.0],
              [100.0, 1.0, 8.0], [100.0, 0.0, 9.0]],
             [[100.2, 0.2, 10.0], [100.8, 0.2, 11.0], [100.8, 0.8, 12.0],
              [100.2, 0.8, 13.0], [100.2, 0.2, 14.0]]],
        ])
        self.mpoly3d_wkb = (
            b'\x01'  # little endian
            b'\xee\x03\x00\x00'  # 3d multipolygon
            b'\x02\x00\x00\x00'  # two polygons
            b'\x01'  # little endian
            b'\xeb\x03\x00\x00'  # 3d polygon
            b'\x01\x00\x00\x00'  # 1 ring
            b'\x05\x00\x00\x00'  # 5 vertices
            b'\x00\x00\x00\x00\x00\x80Y@'
            b'\x00\x00\x00\x00\x00\x00\x00@'
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\xc0Y@'
            b'\x00\x00\x00\x00\x00\x00\x00@'
            b'\x00\x00\x00\x00\x00\x00\xf0?'
            b'\x00\x00\x00\x00\x00\xc0Y@'
            b'\x00\x00\x00\x00\x00\x00\x08@'
            b'\x00\x00\x00\x00\x00\x00\x00@'
            b'\x00\x00\x00\x00\x00\x80Y@'
            b'\x00\x00\x00\x00\x00\x00\x08@'
            b'\x00\x00\x00\x00\x00\x00\x08@'
            b'\x00\x00\x00\x00\x00\x80Y@'
            b'\x00\x00\x00\x00\x00\x00\x00@'
            b'\x00\x00\x00\x00\x00\x00\x10@'
            b'\x01'  # little endian
            b'\xeb\x03\x00\x00'  # 3d polygon
            b'\x02\x00\x00\x00'  # 2 rings
            b'\x05\x00\x00\x00'  # first ring, 5 vertices
            b'\x00\x00\x00\x00\x00\x00Y@'
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x14@'
            b'\x00\x00\x00\x00\x00@Y@'
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x18@'
            b'\x00\x00\x00\x00\x00@Y@'
            b'\x00\x00\x00\x00\x00\x00\xf0?'
            b'\x00\x00\x00\x00\x00\x00\x1c@'
            b'\x00\x00\x00\x00\x00\x00Y@'
            b'\x00\x00\x00\x00\x00\x00\xf0?'
            b'\x00\x00\x00\x00\x00\x00 @'
            b'\x00\x00\x00\x00\x00\x00Y@'
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00"@'
            b'\x05\x00\x00\x00'  # second ring, 5 vertices
            b'\xcd\xcc\xcc\xcc\xcc\x0cY@'
            b'\x9a\x99\x99\x99\x99\x99\xc9?'
            b'\x00\x00\x00\x00\x00\x00$@'
            b'333333Y@'
            b'\x9a\x99\x99\x99\x99\x99\xc9?'
            b'\x00\x00\x00\x00\x00\x00&@'
            b'333333Y@'
            b'\x9a\x99\x99\x99\x99\x99\xe9?'
            b'\x00\x00\x00\x00\x00\x00(@'
            b'\xcd\xcc\xcc\xcc\xcc\x0cY@'
            b'\x9a\x99\x99\x99\x99\x99\xe9?'
            b'\x00\x00\x00\x00\x00\x00*@'
            b'\xcd\xcc\xcc\xcc\xcc\x0cY@'
            b'\x9a\x99\x99\x99\x99\x99\xc9?'
            b'\x00\x00\x00\x00\x00\x00,@'
        )
        self.mpoly4d = dict(type='MultiPolygon', coordinates=[
            [[[102.0, 2.0, 0.0, 14.0], [103.0, 2.0, 1.0, 13.0],
              [103.0, 3.0, 2.0, 12.0], [102.0, 3.0, 3.0, 11.0],
              [102.0, 2.0, 4.0, 10.0]]],
            [[[100.0, 0.0, 5.0, 9.0], [101.0, 0.0, 6.0, 8.0],
              [101.0, 1.0, 7.0, 7.0], [100.0, 1.0, 8.0, 6.0],
              [100.0, 0.0, 9.0, 5.0]],
             [[100.2, 0.2, 10.0, 4.0], [100.8, 0.2, 11.0, 3.0],
              [100.8, 0.8, 12.0, 2.0], [100.2, 0.8, 13.0, 1.0],
              [100.2, 0.2, 14.0, 0.0]]],
        ])
        self.mpoly4d_wkb = (
            b'\x01'  # little endian
            b'\xbe\x0b\x00\x00'  # 4d multipolygon
            b'\x02\x00\x00\x00'  # two polygons
            b'\x01'  # little endian
            b'\xbb\x0b\x00\x00'  # 4d polygon
            b'\x01\x00\x00\x00'  # 1 ring
            b'\x05\x00\x00\x00'  # 5 vertices
            b'\x00\x00\x00\x00\x00\x80Y@'
            b'\x00\x00\x00\x00\x00\x00\x00@'
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00,@'
            b'\x00\x00\x00\x00\x00\xc0Y@'
            b'\x00\x00\x00\x00\x00\x00\x00@'
            b'\x00\x00\x00\x00\x00\x00\xf0?'
            b'\x00\x00\x00\x00\x00\x00*@'
            b'\x00\x00\x00\x00\x00\xc0Y@'
            b'\x00\x00\x00\x00\x00\x00\x08@'
            b'\x00\x00\x00\x00\x00\x00\x00@'
            b'\x00\x00\x00\x00\x00\x00(@'
            b'\x00\x00\x00\x00\x00\x80Y@'
            b'\x00\x00\x00\x00\x00\x00\x08@'
            b'\x00\x00\x00\x00\x00\x00\x08@'
            b'\x00\x00\x00\x00\x00\x00&@'
            b'\x00\x00\x00\x00\x00\x80Y@'
            b'\x00\x00\x00\x00\x00\x00\x00@'
            b'\x00\x00\x00\x00\x00\x00\x10@'
            b'\x00\x00\x00\x00\x00\x00$@'
            b'\x01'  # little endian
            b'\xbb\x0b\x00\x00'  # 4d polygon
            b'\x02\x00\x00\x00'  # 2 rings
            b'\x05\x00\x00\x00'  # first ring, 5 vertices
            b'\x00\x00\x00\x00\x00\x00Y@'
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x14@'
            b'\x00\x00\x00\x00\x00\x00"@'
            b'\x00\x00\x00\x00\x00@Y@'
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x18@'
            b'\x00\x00\x00\x00\x00\x00 @'
            b'\x00\x00\x00\x00\x00@Y@'
            b'\x00\x00\x00\x00\x00\x00\xf0?'
            b'\x00\x00\x00\x00\x00\x00\x1c@'
            b'\x00\x00\x00\x00\x00\x00\x1c@'
            b'\x00\x00\x00\x00\x00\x00Y@'
            b'\x00\x00\x00\x00\x00\x00\xf0?'
            b'\x00\x00\x00\x00\x00\x00 @'
            b'\x00\x00\x00\x00\x00\x00\x18@'
            b'\x00\x00\x00\x00\x00\x00Y@'
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00"@'
            b'\x00\x00\x00\x00\x00\x00\x14@'
            b'\x05\x00\x00\x00'  # second ring, 5 vertices
            b'\xcd\xcc\xcc\xcc\xcc\x0cY@'
            b'\x9a\x99\x99\x99\x99\x99\xc9?'
            b'\x00\x00\x00\x00\x00\x00$@'
            b'\x00\x00\x00\x00\x00\x00\x10@'
            b'333333Y@'
            b'\x9a\x99\x99\x99\x99\x99\xc9?'
            b'\x00\x00\x00\x00\x00\x00&@'
            b'\x00\x00\x00\x00\x00\x00\x08@'
            b'333333Y@'
            b'\x9a\x99\x99\x99\x99\x99\xe9?'
            b'\x00\x00\x00\x00\x00\x00(@'
            b'\x00\x00\x00\x00\x00\x00\x00@'
            b'\xcd\xcc\xcc\xcc\xcc\x0cY@'
            b'\x9a\x99\x99\x99\x99\x99\xe9?'
            b'\x00\x00\x00\x00\x00\x00*@'
            b'\x00\x00\x00\x00\x00\x00\xf0?'
            b'\xcd\xcc\xcc\xcc\xcc\x0cY@'
            b'\x9a\x99\x99\x99\x99\x99\xc9?'
            b'\x00\x00\x00\x00\x00\x00,@'
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
        )

        self.mpoly2d_srid4326 = dict(
            type='MultiPolygon',
            coordinates=[
                [[[102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0],
                  [102.0, 2.0]]],
                [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0],
                  [100.0, 0.0]],
                 [[100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8],
                  [100.2, 0.2]]],
            ],
            meta=dict(srid=4326),
            crs={'properties': {'name': 'EPSG4326'}, 'type': 'name'},
        )
        self.mpoly2d_srid4326_wkb = (
            b'\x01'  # little endian
            b'\x06\x00\x00\x20'  # 2d multipolygon wth SRID flag
            b'\xe6\x10\x00\x00'  # 4 bytes containing SRID (SRID=4326)
            b'\x02\x00\x00\x00'  # two polygons
            b'\x01'  # little endian
            b'\x03\x00\x00\x00'  # 2d polygon
            b'\x01\x00\x00\x00'  # 1 ring
            b'\x05\x00\x00\x00'  # 5 vertices
            b'\x00\x00\x00\x00\x00\x80Y@'
            b'\x00\x00\x00\x00\x00\x00\x00@'
            b'\x00\x00\x00\x00\x00\xc0Y@'
            b'\x00\x00\x00\x00\x00\x00\x00@'
            b'\x00\x00\x00\x00\x00\xc0Y@'
            b'\x00\x00\x00\x00\x00\x00\x08@'
            b'\x00\x00\x00\x00\x00\x80Y@'
            b'\x00\x00\x00\x00\x00\x00\x08@'
            b'\x00\x00\x00\x00\x00\x80Y@'
            b'\x00\x00\x00\x00\x00\x00\x00@'
            b'\x01'  # little endian
            b'\x03\x00\x00\x00'  # 2d polygon
            b'\x02\x00\x00\x00'  # 2 rings
            b'\x05\x00\x00\x00'  # first ring, 5 vertices
            b'\x00\x00\x00\x00\x00\x00Y@'
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00@Y@'
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00@Y@'
            b'\x00\x00\x00\x00\x00\x00\xf0?'
            b'\x00\x00\x00\x00\x00\x00Y@'
            b'\x00\x00\x00\x00\x00\x00\xf0?'
            b'\x00\x00\x00\x00\x00\x00Y@'
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x05\x00\x00\x00'  # second ring, 5 vertices
            b'\xcd\xcc\xcc\xcc\xcc\x0cY@'
            b'\x9a\x99\x99\x99\x99\x99\xc9?'
            b'333333Y@'
            b'\x9a\x99\x99\x99\x99\x99\xc9?'
            b'333333Y@'
            b'\x9a\x99\x99\x99\x99\x99\xe9?'
            b'\xcd\xcc\xcc\xcc\xcc\x0cY@'
            b'\x9a\x99\x99\x99\x99\x99\xe9?'
            b'\xcd\xcc\xcc\xcc\xcc\x0cY@'
            b'\x9a\x99\x99\x99\x99\x99\xc9?'
        )

    def test_dumps_2d(self):
        self.assertEqual(self.mpoly2d_wkb,
                         wkb.dumps(self.mpoly2d, big_endian=False))

    def test_dumps_3d(self):
        self.assertEqual(self.mpoly3d_wkb,
                         wkb.dumps(self.mpoly3d, big_endian=False))

    def test_dumps_4d(self):
        self.assertEqual(self.mpoly4d_wkb,
                         wkb.dumps(self.mpoly4d, big_endian=False))

    def test_dumps_2d_srid4326(self):
        self.assertEqual(
            self.mpoly2d_srid4326_wkb,
            wkb.dumps(self.mpoly2d_srid4326, big_endian=False),
        )

    def test_loads_2d(self):
        self.assertEqual(self.mpoly2d, wkb.loads(self.mpoly2d_wkb))

    def test_loads_z(self):
        self.assertEqual(self.mpoly3d, wkb.loads(self.mpoly3d_wkb))

    def test_loads_m(self):
        exp_mpoly = self.mpoly3d.copy()
        for polygon in exp_mpoly['coordinates']:
            for ring in polygon:
                for vert in ring:
                    vert.insert(2, 0.0)

        mpoly_wkb = (
            b'\x01'  # little endian
            b'\xd6\x07\x00\x00'  # m multipolygon
            b'\x02\x00\x00\x00'  # two polygons
            b'\x01'  # little endian
            b'\xd3\x07\x00\x00'  # m polygon
            b'\x01\x00\x00\x00'  # 1 ring
            b'\x05\x00\x00\x00'  # 5 vertices
            b'\x00\x00\x00\x00\x00\x80Y@'
            b'\x00\x00\x00\x00\x00\x00\x00@'
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\xc0Y@'
            b'\x00\x00\x00\x00\x00\x00\x00@'
            b'\x00\x00\x00\x00\x00\x00\xf0?'
            b'\x00\x00\x00\x00\x00\xc0Y@'
            b'\x00\x00\x00\x00\x00\x00\x08@'
            b'\x00\x00\x00\x00\x00\x00\x00@'
            b'\x00\x00\x00\x00\x00\x80Y@'
            b'\x00\x00\x00\x00\x00\x00\x08@'
            b'\x00\x00\x00\x00\x00\x00\x08@'
            b'\x00\x00\x00\x00\x00\x80Y@'
            b'\x00\x00\x00\x00\x00\x00\x00@'
            b'\x00\x00\x00\x00\x00\x00\x10@'
            b'\x01'  # little endian
            b'\xd3\x07\x00\x00'  # m polygon
            b'\x02\x00\x00\x00'  # 2 rings
            b'\x05\x00\x00\x00'  # first ring, 5 vertices
            b'\x00\x00\x00\x00\x00\x00Y@'
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x14@'
            b'\x00\x00\x00\x00\x00@Y@'
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x18@'
            b'\x00\x00\x00\x00\x00@Y@'
            b'\x00\x00\x00\x00\x00\x00\xf0?'
            b'\x00\x00\x00\x00\x00\x00\x1c@'
            b'\x00\x00\x00\x00\x00\x00Y@'
            b'\x00\x00\x00\x00\x00\x00\xf0?'
            b'\x00\x00\x00\x00\x00\x00 @'
            b'\x00\x00\x00\x00\x00\x00Y@'
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00"@'
            b'\x05\x00\x00\x00'  # second ring, 5 vertices
            b'\xcd\xcc\xcc\xcc\xcc\x0cY@'
            b'\x9a\x99\x99\x99\x99\x99\xc9?'
            b'\x00\x00\x00\x00\x00\x00$@'
            b'333333Y@'
            b'\x9a\x99\x99\x99\x99\x99\xc9?'
            b'\x00\x00\x00\x00\x00\x00&@'
            b'333333Y@'
            b'\x9a\x99\x99\x99\x99\x99\xe9?'
            b'\x00\x00\x00\x00\x00\x00(@'
            b'\xcd\xcc\xcc\xcc\xcc\x0cY@'
            b'\x9a\x99\x99\x99\x99\x99\xe9?'
            b'\x00\x00\x00\x00\x00\x00*@'
            b'\xcd\xcc\xcc\xcc\xcc\x0cY@'
            b'\x9a\x99\x99\x99\x99\x99\xc9?'
            b'\x00\x00\x00\x00\x00\x00,@'
        )
        self.assertEqual(exp_mpoly, wkb.loads(mpoly_wkb))

    def test_loads_zm(self):
        self.assertEqual(self.mpoly4d, wkb.loads(self.mpoly4d_wkb))

    def test_loads_2d_srid4326(self):
        self.assertEqual(
            self.mpoly2d_srid4326,
            wkb.loads(self.mpoly2d_srid4326_wkb),
        )


class GeometryCollectionTestCase(unittest.TestCase):

    def setUp(self):
        self.gc2d = dict(type='GeometryCollection', geometries=[
            dict(type='Point', coordinates=[0.0, 1.0]),
            dict(type='LineString', coordinates=[
                [102.0, 2.0], [103.0, 3.0], [104.0, 4.0]
            ]),
        ])
        self.gc2d_wkb = (
            b'\x00'  # big endian
            b'\x00\x00\x00\x07'  # 2d geometry collection
            b'\x00\x00\x00\x02'  # 2 geometries in the collection
            b'\x00'
            b'\x00\x00\x00\x01'  # 2d point
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'?\xf0\x00\x00\x00\x00\x00\x00'
            b'\x00'
            b'\x00\x00\x00\x02'  # 2d linestring
            b'\x00\x00\x00\x03'  # 3 vertices
            b'@Y\x80\x00\x00\x00\x00\x00'
            b'@\x00\x00\x00\x00\x00\x00\x00'
            b'@Y\xc0\x00\x00\x00\x00\x00'
            b'@\x08\x00\x00\x00\x00\x00\x00'
            b'@Z\x00\x00\x00\x00\x00\x00'
            b'@\x10\x00\x00\x00\x00\x00\x00'
        )
        self.gc3d = dict(type='GeometryCollection', geometries=[
            dict(type='Point', coordinates=[0.0, 1.0, 2.0]),
            dict(type='LineString', coordinates=[
                [102.0, 2.0, 6.0], [103.0, 3.0, 7.0], [104.0, 4.0, 8.0]
            ]),
        ])
        self.gc3d_wkb = (
            b'\x01'  # little endian
            b'\xef\x03\x00\x00'  # 3d geometry collection
            b'\x02\x00\x00\x00'  # 2 geometries in the collection
            b'\x01'
            b'\xe9\x03\x00\x00'  # 3d point
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\xf0?'
            b'\x00\x00\x00\x00\x00\x00\x00@'
            b'\x01'
            b'\xea\x03\x00\x00'  # 3d linestring
            b'\x03\x00\x00\x00'  # 3 vertices
            b'\x00\x00\x00\x00\x00\x80Y@'
            b'\x00\x00\x00\x00\x00\x00\x00@'
            b'\x00\x00\x00\x00\x00\x00\x18@'
            b'\x00\x00\x00\x00\x00\xc0Y@'
            b'\x00\x00\x00\x00\x00\x00\x08@'
            b'\x00\x00\x00\x00\x00\x00\x1c@'
            b'\x00\x00\x00\x00\x00\x00Z@'
            b'\x00\x00\x00\x00\x00\x00\x10@'
            b'\x00\x00\x00\x00\x00\x00 @'
        )
        self.gc4d = dict(type='GeometryCollection', geometries=[
            dict(type='Point', coordinates=[0.0, 1.0, 2.0, 3.0]),
            dict(type='LineString', coordinates=[
                [102.0, 2.0, 6.0, 10.0], [103.0, 3.0, 7.0, 11.0],
                [104.0, 4.0, 8.0, 12.0]
            ]),
        ])
        self.gc4d_wkb = (
            b'\x00'  # big endian
            b'\x00\x00\x0b\xbf'  # 4d geometry collection
            b'\x00\x00\x00\x02'  # 2 geometries in the collection
            b'\x00'
            b'\x00\x00\x0b\xb9'  # 4d point
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'?\xf0\x00\x00\x00\x00\x00\x00'
            b'@\x00\x00\x00\x00\x00\x00\x00'
            b'@\x08\x00\x00\x00\x00\x00\x00'
            b'\x00'
            b'\x00\x00\x0b\xba'  # 4d linestring
            b'\x00\x00\x00\x03'  # 3 vertices
            b'@Y\x80\x00\x00\x00\x00\x00'
            b'@\x00\x00\x00\x00\x00\x00\x00'
            b'@\x18\x00\x00\x00\x00\x00\x00'
            b'@$\x00\x00\x00\x00\x00\x00'
            b'@Y\xc0\x00\x00\x00\x00\x00'
            b'@\x08\x00\x00\x00\x00\x00\x00'
            b'@\x1c\x00\x00\x00\x00\x00\x00'
            b'@&\x00\x00\x00\x00\x00\x00'
            b'@Z\x00\x00\x00\x00\x00\x00'
            b'@\x10\x00\x00\x00\x00\x00\x00'
            b'@ \x00\x00\x00\x00\x00\x00'
            b'@(\x00\x00\x00\x00\x00\x00'
        )

        self.gc2d_srid1234 = dict(
            type='GeometryCollection',
            geometries=[
                dict(type='Point', coordinates=[0.0, 1.0]),
                dict(type='LineString', coordinates=[
                    [102.0, 2.0], [103.0, 3.0], [104.0, 4.0]
                ]),
            ],
            meta=dict(srid=1234),
            crs={'properties': {'name': 'EPSG1234'}, 'type': 'name'},
        )

        self.gc2d_srid1234_wkb = (
            b'\x00'  # big endian
            b'\x20\x00\x00\x07'  # 2d geometry collection
            b'\x00\x00\x04\xd2'  # srid 1234
            b'\x00\x00\x00\x02'  # 2 geometries in the collection
            b'\x00'  # big endian
            b'\x00\x00\x00\x01'  # 2d point
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'?\xf0\x00\x00\x00\x00\x00\x00'
            b'\x00'  # big endian
            b'\x00\x00\x00\x02'  # 2d linestring
            b'\x00\x00\x00\x03'  # 3 vertices
            b'@Y\x80\x00\x00\x00\x00\x00'
            b'@\x00\x00\x00\x00\x00\x00\x00'
            b'@Y\xc0\x00\x00\x00\x00\x00'
            b'@\x08\x00\x00\x00\x00\x00\x00'
            b'@Z\x00\x00\x00\x00\x00\x00'
            b'@\x10\x00\x00\x00\x00\x00\x00'
        )

    def test_dumps_2d(self):
        self.assertEqual(self.gc2d_wkb, wkb.dumps(self.gc2d))

    def test_dumps_3d(self):
        self.assertEqual(self.gc3d_wkb, wkb.dumps(self.gc3d, big_endian=False))

    def test_dumps_4d(self):
        self.assertEqual(self.gc4d_wkb, wkb.dumps(self.gc4d))

    def test_dumps_2d_srid1234(self):
        self.assertEqual(self.gc2d_srid1234_wkb, wkb.dumps(self.gc2d_srid1234))

    def test_loads_2d(self):
        self.assertEqual(self.gc2d, wkb.loads(self.gc2d_wkb))

    def test_loads_z(self):
        self.assertEqual(self.gc3d, wkb.loads(self.gc3d_wkb))

    def test_loads_m(self):
        exp_gc = dict(type='GeometryCollection', geometries=[
            dict(type='Point', coordinates=[0.0, 1.0, 0.0, 2.0]),
            dict(type='LineString', coordinates=[
                [102.0, 2.0, 0.0, 6.0], [103.0, 3.0, 0.0, 7.0],
                [104.0, 4.0, 0.0, 8.0]
            ]),
        ])
        gc_wkb = (
            b'\x01'  # little endian
            b'\xd7\x07\x00\x00'
            b'\x02\x00\x00\x00'  # 2 geometries in the collection
            b'\x01'
            b'\xd1\x07\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\xf0?'
            b'\x00\x00\x00\x00\x00\x00\x00@'
            b'\x01'
            b'\xd2\x07\x00\x00'
            b'\x03\x00\x00\x00'  # 3 vertices
            b'\x00\x00\x00\x00\x00\x80Y@'
            b'\x00\x00\x00\x00\x00\x00\x00@'
            b'\x00\x00\x00\x00\x00\x00\x18@'
            b'\x00\x00\x00\x00\x00\xc0Y@'
            b'\x00\x00\x00\x00\x00\x00\x08@'
            b'\x00\x00\x00\x00\x00\x00\x1c@'
            b'\x00\x00\x00\x00\x00\x00Z@'
            b'\x00\x00\x00\x00\x00\x00\x10@'
            b'\x00\x00\x00\x00\x00\x00 @'
        )
        self.assertEqual(exp_gc, wkb.loads(gc_wkb))

    def test_loads_zm(self):
        self.assertEqual(self.gc4d, wkb.loads(self.gc4d_wkb))

    def test_loads_2d_srid1234(self):
        self.assertEqual(self.gc2d_srid1234, wkb.loads(self.gc2d_srid1234_wkb))
