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

from geomet import util


class PointRoundingTestCase(unittest.TestCase):

    def setUp(self):
        self.point = {
            'coordinates': (0.7071067811865481, -0.707106781186547),
            'type': 'Point'}

    def test_round1(self):
        expectation = {
            'coordinates': (0.7, -0.7),
            'type': 'Point'}
        rounded = util.round_geom(self.point, 1)
        self.assertEqual(rounded, expectation)


class LineStringRoundingTestCase(unittest.TestCase):

    def setUp(self):
        # The testing LineString is the product of
        # shapely.geometry.Point(0, 0).buffer(1.0, 2).exterior.
        self.linestring = {
            'coordinates': (
                (1.0, 0.0),
                (0.7071067811865481, -0.707106781186547),
                (1.6155445744325867e-15, -1.0),
                (-0.7071067811865459, -0.7071067811865492),
                (-1.0, -3.2310891488651735e-15),
                (-0.7071067811865505, 0.7071067811865446),
                (-4.624589118372729e-15, 1.0),
                (0.7071067811865436, 0.7071067811865515),
                (1.0, 0.0)),
            'type': 'LineString'}

    def test_round1(self):
        expectation = {
            'coordinates': (
                (1.0, 0.0),
                (0.7, -0.7),
                (0.0, -1.0),
                (-0.7, -0.7),
                (-1.0, 0.0),
                (-0.7, 0.7),
                (0.0, 1.0),
                (0.7, 0.7),
                (1.0, 0.0)),
            'type': 'LineString'}
        rounded = util.round_geom(self.linestring, 1)
        self.assertEqual(rounded, expectation)

    def test_round2(self):
        expectation = {
            'coordinates': (
                (1.0, 0.0),
                (0.71, -0.71),
                (0.0, -1.0),
                (-0.71, -0.71),
                (-1.0, 0.0),
                (-0.71, 0.71),
                (0.0, 1.0),
                (0.71, 0.71),
                (1.0, 0.0)),
            'type': 'LineString'}
        rounded = util.round_geom(self.linestring, 2)
        self.assertEqual(rounded, expectation)


class PolygonRoundingTestCase(unittest.TestCase):

    def setUp(self):
        # The testing Polygon is the product of
        # shapely.geometry.Point(0, 0).buffer(1.0, 2).
        self.polygon = {
            'coordinates': [(
                (1.0, 0.0),
                (0.7071067811865481, -0.707106781186547),
                (1.6155445744325867e-15, -1.0),
                (-0.7071067811865459, -0.7071067811865492),
                (-1.0, -3.2310891488651735e-15),
                (-0.7071067811865505, 0.7071067811865446),
                (-4.624589118372729e-15, 1.0),
                (0.7071067811865436, 0.7071067811865515),
                (1.0, 0.0))],
            'type': 'Polygon'}

    def test_round1(self):
        expectation = {
            'coordinates': [(
                (1.0, 0.0),
                (0.7, -0.7),
                (0.0, -1.0),
                (-0.7, -0.7),
                (-1.0, 0.0),
                (-0.7, 0.7),
                (0.0, 1.0),
                (0.7, 0.7),
                (1.0, 0.0))],
            'type': 'Polygon'}
        rounded = util.round_geom(self.polygon, 1)
        self.assertEqual(rounded, expectation)

    def test_round2(self):
        expectation = {
            'coordinates': [(
                (1.0, 0.0),
                (0.71, -0.71),
                (0.0, -1.0),
                (-0.71, -0.71),
                (-1.0, 0.0),
                (-0.71, 0.71),
                (0.0, 1.0),
                (0.71, 0.71),
                (1.0, 0.0))],
            'type': 'Polygon'}
        rounded = util.round_geom(self.polygon, 2)
        self.assertEqual(rounded, expectation)


class MultiPolygonRoundingTestCase(unittest.TestCase):

    def setUp(self):
        # The testing MultiPolygon is the product of
        # shapely.geometry.Point(0, 0).buffer(1.0, 2).
        self.multipolygon = {
            'coordinates': [[(
                (1.0, 0.0),
                (0.7071067811865481, -0.707106781186547),
                (1.6155445744325867e-15, -1.0),
                (-0.7071067811865459, -0.7071067811865492),
                (-1.0, -3.2310891488651735e-15),
                (-0.7071067811865505, 0.7071067811865446),
                (-4.624589118372729e-15, 1.0),
                (0.7071067811865436, 0.7071067811865515),
                (1.0, 0.0))]],
            'type': 'MultiPolygon'}

    def test_round1(self):
        expectation = {
            'coordinates': [[(
                (1.0, 0.0),
                (0.7, -0.7),
                (0.0, -1.0),
                (-0.7, -0.7),
                (-1.0, 0.0),
                (-0.7, 0.7),
                (0.0, 1.0),
                (0.7, 0.7),
                (1.0, 0.0))]],
            'type': 'MultiPolygon'}
        rounded = util.round_geom(self.multipolygon, 1)
        self.assertEqual(rounded, expectation)


class FlattenMultiDimTestCase(unittest.TestCase):

    def test_1d(self):
        data = [1, 2, 3]
        self.assertEqual(data, list(util.flatten_multi_dim(data)))

    def test_2d(self):
        data = [[1, 2], [3, 4, 5]]
        expected = [1, 2, 3, 4, 5]
        self.assertEqual(expected, list(util.flatten_multi_dim(data)))

    def test_multid(self):
        data = [[[1], [2, 3]], [4, 5, [6]]]
        expected = [1, 2, 3, 4, 5, 6]
        self.assertEqual(expected, list(util.flatten_multi_dim(data)))
