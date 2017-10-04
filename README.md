GeoMet [![Build Status](https://secure.travis-ci.org/geomet/geomet.png?branch=master)](http://travis-ci.org/geomet/geomet)
======

Convert [GeoJSON](http://www.geojson.org/geojson-spec.html) to
[WKT/WKB](http://en.wikipedia.org/wiki/Well-known_text) (Well-Known
Text/Binary), and vice versa. [Extended WKB/WKT](https://postgis.net/docs/using_postgis_dbmanagement.html#EWKB_EWKT)
are also supported. Conversion functions are exposed through
idiomatic `load/loads/dump/dumps` interfaces.

The name "GeoMet" was inspired by "met", the German word for
[mead](http://en.wikipedia.org/wiki/Mead). It is also a shortened version of
the word "geometry".

GeoMet is intended to cover all common use cases for dealing with 2D, 3D, and
4D geometries (including 'Z', 'M', and 'ZM').

The following conversion functions are supported.

WKT/EWKT <--> GeoJSON:

- Point
- LineString
- Polygon
- MultiPoint
- MultiLineString
- MultiPolygon
- GeometryCollection

WKB/EWKB <--> GeoJSON:

- Point
- LineString
- Polygon
- MultiPoint
- MultiLineString
- MultiPolygon
- GeometryCollection

### Installation ###

Install from [PyPI](https://pypi.python.org/pypi) (easiest method):

    $ pip install geomet

Clone the source code from git and run:

    $ python setup.py install

You can also install directly from the git repo using pip:

    $ pip install git+git://github.com/geomet/geomet.git

### Example usage ###

Coverting a 'Point' GeoJSON object to WKT:

    >>> from geomet import wkt
    >>> point = {'type': 'Point', 'coordinates': [116.4, 45.2, 11.1]}
    >>> wkt.dumps(point, decimals=4)
    'POINT (116.4000 45.2000 11.1000)'

Converting a 'Point' GeoJSON object to WKB:

    >>> from geomet import wkb
    >>> wkb.dumps(point)
    '\x00\x00\x00\x10\x01@]\x19\x99\x99\x99\x99\x9a@F\x99\x99\x99\x99\x99\x9a@&333333'
    >>> wkb.dumps(point, big_endian=False)
    '\x01\x01\x10\x00\x00\x9a\x99\x99\x99\x99\x19]@\x9a\x99\x99\x99\x99\x99F@333333&@'

Converting a 'LineString' GeoJSON object to WKT:

    >>> linestring = {'type':'LineString',
    ...               'coordinates': [[0.0, 0.0, 10.0], [2.0, 1.0, 20.0],
    ...                               [4.0, 2.0, 30.0], [5.0, 4.0, 40.0]]}
    >>> wkt.dumps(linestring, decimals=0)
    'LINESTRING (0 0 10, 2 1 20, 4 2 30, 5 4 40)'

Converting a 'LineString' GeoJSON object to WKB:

    >>> wkb.dumps(linestring)
    '\x00\x00\x00\x10\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00@$\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00@4\x00\x00\x00\x00\x00\x00@\x10\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00@>\x00\x00\x00\x00\x00\x00@\x14\x00\x00\x00\x00\x00\x00@\x10\x00\x00\x00\x00\x00\x00@D\x00\x00\x00\x00\x00\x00'
    >>> wkb.dumps(linestring, big_endian=False)
    '\x01\x02\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00$@\x00\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x004@\x00\x00\x00\x00\x00\x00\x10@\x00\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00>@\x00\x00\x00\x00\x00\x00\x14@\x00\x00\x00\x00\x00\x00\x10@\x00\x00\x00\x00\x00\x00D@'

Converting 'Point' WKT to GeoJSON:

    >>> wkt.loads('POINT(10 20)')
    {'type': 'Point', 'coordinates': [10.0, 20.0]}

Coverting 'GeometryCollection' WKT to GeoJSON:

    >>> wkt.loads('GEOMETRYCOLLECTION(POINT(10 20),POLYGON(((0 0), (10 30), (30 10), (0 0)))')
    {'type': 'GeometryCollection', 'geometries': [{'type': 'Point', 'coordinates': [10.0, 20.0]}, {'type': 'Polygon', 'coordinates': [[[0.0, 0.0]], [[10.0, 30.0]], [[30.0, 10.0]], [[0.0, 0.0]]]}]}

EWKT/EWKB are also supported for all geometry types. This uses a custom extension
to the GeoJSON standard in order to preserve SRID information through conversions.
For example:

    >>> wkt.loads('SRID=4326;POINT(10 20)')
    {'type': 'Point', 'coordinates': [10.0, 20.0], 'meta': {'srid': '4326'}}
    >>> wkt.dumps({'type': 'Point', 'coordinates': [10.0, 20.0], 'meta': {'srid': '4326'}, 'crs': {'properties': {'name': 'EPSG4326'}, 'type': 'name'}})
    'SRID=4326;POINT (10.0000000000000000 20.0000000000000000)'
    >>> wkb.loads('\x00 \x00\x00\x01\x00\x00\x10\xe6@$\x00\x00\x00\x00\x00\x00@4\x00\x00\x00\x00\x00\x00')
    {'meta': {'srid': '4326'}, 'type': 'Point', 'coordinates': [10.0, 20.0]}
    >>> wkb.dumps({'type': 'Point', 'coordinates': [10.0, 20.0], 'meta': {'srid': '4326'}, 'crs': {'properties': {'name': 'EPSG4326'}, 'type': 'name'}})
    '\x00 \x00\x00\x01\x00\x00\x10\xe6@$\x00\x00\x00\x00\x00\x00@4\x00\x00\x00\x00\x00\x00'


### See Also ###

- [wellknown](https://github.com/mapbox/wellknown): A similar package for Node.js.
- [geo](https://github.com/bryanjos/geo): A nearly-identical package for Elixir.
