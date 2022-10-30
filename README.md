# GeoMet [![geomet](https://circleci.com/gh/geomet/geomet.svg?style=shield)](https://app.circleci.com/pipelines/github/geomet)

Pure-Python conversion library for common geospatial data formats.
Supported formats include:
- [GeoJSON](http://www.geojson.org/geojson-spec.html)
- [WKT/WKB](http://en.wikipedia.org/wiki/Well-known_text) (Well-Known Text/Binary)
- [Extended WKB/WKT](https://postgis.net/docs/using_postgis_dbmanagement.html#EWKB_EWKT)
- [GeoPackage Binary](http://www.geopackage.org/spec/#gpb_format)


## Install

Install the latest version from [PyPI](https://pypi.org/project/geomet/):

    $ pip install geomet

## Functionality

Converion functions are exposed through idiomatic `load/loads/dump/dumps`
interfaces.

GeoMet is intended to cover all common use cases for dealing with 2D, 3D, and
4D geometries (including 'Z', 'M', and 'ZM').

| Geometry | WKT/EWKT | WKB/EWKB | GeoPackage Binary | EsriJSON |
| -------- | :------: | :------: | :---------------: | :------: |
| Point    | ✅ | ✅ | ✅| ✅ |
| LineString    | ✅ | ✅ | ✅| ✅ |
| Polygon    | ✅ | ✅ | ✅| ✅ |
| MultiPoint    | ✅ | ✅ | ✅| ✅ |
| MultiLineString    | ✅ | ✅ | ✅| ✅ |
| MultiPolygon    | ✅ | ✅ | ✅| ✅ |
| GeometryCollection    | ✅ | ✅ | ✅| ✅ |

## Example usage

Coverting a 'Point' GeoJSON object to WKT:

    >>> from geomet import wkt
    >>> point = {'type': 'Point', 'coordinates': [116.4, 45.2, 11.1]}
    >>> wkt.dumps(point, decimals=4)
    'POINT (116.4000 45.2000 11.1000)'

Converting a 'Point' GeoJSON object to WKB:

    >>> from geomet import wkb
    >>> wkb.dumps(point)
    b'\x00\x00\x00\x10\x01@]\x19\x99\x99\x99\x99\x9a@F\x99\x99\x99\x99\x99\x9a@&333333'
    >>> wkb.dumps(point, big_endian=False)
    b'\x01\x01\x10\x00\x00\x9a\x99\x99\x99\x99\x19]@\x9a\x99\x99\x99\x99\x99F@333333&@'

Converting a 'Point' GeoJSON object to GeoPackage Binary:

    >>> from geomet import geopackage
    >>> geopackage.dumps(point)
    b'GP\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xe9@]\x19\x99\x99\x99\x99\x9a@F\x99\x99\x99\x99\x99\x9a@&333333'
    >>> geopackage.dumps(point, big_endian=False)
    b'GP\x00\x01\x00\x00\x00\x00\x01\xe9\x03\x00\x00\x9a\x99\x99\x99\x99\x19]@\x9a\x99\x99\x99\x99\x99F@333333&@'


Converting a 'LineString' GeoJSON object to WKT:

    >>> linestring = {'type':'LineString',
    ...               'coordinates': [[0.0, 0.0, 10.0], [2.0, 1.0, 20.0],
    ...                               [4.0, 2.0, 30.0], [5.0, 4.0, 40.0]]}
    >>> wkt.dumps(linestring, decimals=0)
    'LINESTRING (0 0 10, 2 1 20, 4 2 30, 5 4 40)'

Converting a 'LineString' GeoJSON object to WKB:

    >>> wkb.dumps(linestring)
    b'\x00\x00\x00\x10\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00@$\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00@4\x00\x00\x00\x00\x00\x00@\x10\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00@>\x00\x00\x00\x00\x00\x00@\x14\x00\x00\x00\x00\x00\x00@\x10\x00\x00\x00\x00\x00\x00@D\x00\x00\x00\x00\x00\x00'
    >>> wkb.dumps(linestring, big_endian=False)
    b'\x01\x02\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00$@\x00\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x004@\x00\x00\x00\x00\x00\x00\x10@\x00\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00>@\x00\x00\x00\x00\x00\x00\x14@\x00\x00\x00\x00\x00\x00\x10@\x00\x00\x00\x00\x00\x00D@'

Converting a 'LineString' GeoJSON object to GeoPackage Binary:

    >>> geopackage.dumps(linestring)
    b'GP\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00@$\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00@4\x00\x00\x00\x00\x00\x00@\x10\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00@>\x00\x00\x00\x00\x00\x00@\x14\x00\x00\x00\x00\x00\x00@\x10\x00\x00\x00\x00\x00\x00@D\x00\x00\x00\x00\x00\x00'
    >>> geopackage.dumps(linestring, big_endian=False)
    b'GP\x00\x01\x00\x00\x00\x00\x01\x02\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00$@\x00\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x004@\x00\x00\x00\x00\x00\x00\x10@\x00\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00>@\x00\x00\x00\x00\x00\x00\x14@\x00\x00\x00\x00\x00\x00\x10@\x00\x00\x00\x00\x00\x00D@'

Converting 'Point' WKT to GeoJSON:

    >>> wkt.loads('POINT(10 20)')
    {'type': 'Point', 'coordinates': [10.0, 20.0]}

Coverting 'GeometryCollection' WKT to GeoJSON:

    >>> wkt.loads('GEOMETRYCOLLECTION(POINT(10 20),POLYGON(((0 0), (10 30), (30 10), (0 0)))')
    {'type': 'GeometryCollection', 'geometries': [{'type': 'Point', 'coordinates': [10.0, 20.0]}, {'type': 'Polygon', 'coordinates': [[[0.0, 0.0]], [[10.0, 30.0]], [[30.0, 10.0]], [[0.0, 0.0]]]}]}

[EWKT/EWKB](http://postgis.net/documentation/manual-2.1/using_postgis_dbmanagement.html#EWKB_EWKT) 
are also supported for all geometry types. This uses a custom extension
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

GeoPackage binary supports encoding of SRID and envelope information. If your geopackage
has an envelope specified, then it will be added into the resulting GeoJSON in a key 
called `'bbox'`:

    >>> gpkg = b'GP\x00\x03\x00\x00\x00\x00\xf0\x9e\xa0\xa7\x05;#@hZ\xbd\x93\x83GC@\xf0\x9e\xa0\xa7\x05;#@hZ\xbd\x93\x83GC@\x01\x01\x00\x00\x00\xf0\x9e\xa0\xa7\x05;#@hZ\xbd\x93\x83GC@'
    >>> geopackage.loads(gpkg)
    >>> {'type': 'Point', 'coordinates': [9.615277517659223, 38.55870291467437], 'bbox': (9.615277517659223, 38.55870291467437, 9.615277517659223, 38.55870291467437)}
    
In the same way, if a 'bbox' key is present on a `dumps`-ed geometry, it will be added to the 
header of the GeoPackage geometry:

    >>> polygon = {'type': 'Polygon', 'coordinates': [[[20.0, 20.0], [34.0, 124.0], [70.0, 140.0], [130.0, 130.0], [70.0, 100.0], [110.0, 70.0], [170.0, 20.0], [90.0, 10.0], [20.0, 20.0]]], 'bbox': (20.0, 170.0, 10.0, 140.0)}
    >>> geopackage.dumps(polygon)
    b'GP\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x004@\x00\x00\x00\x00\x00@e@\x00\x00\x00\x00\x00\x00$@\x00\x00\x00\x00\x00\x80a@\x00\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00\t@4\x00\x00\x00\x00\x00\x00@4\x00\x00\x00\x00\x00\x00@A\x00\x00\x00\x00\x00\x00@_\x00\x00\x00\x00\x00\x00@Q\x80\x00\x00\x00\x00\x00@a\x80\x00\x00\x00\x00\x00@`@\x00\x00\x00\x00\x00@`@\x00\x00\x00\x00\x00@Q\x80\x00\x00\x00\x00\x00@Y\x00\x00\x00\x00\x00\x00@[\x80\x00\x00\x00\x00\x00@Q\x80\x00\x00\x00\x00\x00@e@\x00\x00\x00\x00\x00@4\x00\x00\x00\x00\x00\x00@V\x80\x00\x00\x00\x00\x00@$\x00\x00\x00\x00\x00\x00@4\x00\x00\x00\x00\x00\x00@4\x00\x00\x00\x00\x00\x00'

If an integer SRID identifier is present in a `'meta'` key (like `'meta': {'srid': 4326}`), then the SRID will be included in the
GeoPackage header.

## History

This library was originally created as the result of a bug report related
to another project: https://bugs.launchpad.net/openquake-old/+bug/1073909.
The source of this issue was largely due to a dependency on
[GEOS](https://libgeos.org/), which is written in C/C++. Depending on GEOS
requires any data conversion bug fixes to happen upstream, which takes time
and effort. Ultimately, this was the inspiration to create a more
lightweight, pure-Python conversion library as an alterntive tool for
reliably converting data between various geospatial formats.

The name "GeoMet" was inspired by "met", the German word for
[mead](http://en.wikipedia.org/wiki/Mead). It is also a shortened version of
the word "geometry".

## Limitations

### Outputing "empty" geometries to binary formats is not supported

Attempting to output an empty geometry to a binary format will result in an exception: `ValueError: Empty geometries cannot be represented in WKB. Reason: The dimensionality of the WKB would be ambiguous.` There are a few reasons for this this limitation:
- Any `EMTPY` geometry (e.g., `POINT EMPTY`, `MULTIPOLYGON EMPTY`, etc.) cannot be converted into binary format because binary formats such as WKB require an explicit dimension type (2d, Z, M, or ZM). This means that some objects cannot be reliably converted to and from different formats in a [bijective](https://en.wikipedia.org/wiki/Bijection) manner.
- The [GeoJSON standard](https://www.rfc-editor.org/rfc/rfc7946) does have a way of representing empty geometries; however, details are minimal and the dimensionality of such an object remains ambiguous.
- Representing some geometry types (such as points and lines) as "empty" is [deeply flawed to begin with](http://aleph0.clarku.edu/~djoyce/elements/bookI/defI1.html). For example, a point can represent any location in 2d, 3d, or 4d space. However, a point is infinitesimally small (it has no size) and it can't contain anything (it can't be "full"), therefore, it doesn't make sense for a point to be "empty".

As a result, GeoMet has chosen to not attempt to address these problems, and
simply raise an exception instead.

Example:

    >>> import geomet
    >>> import geomet.wkt as wkt
    >>> import geomet.wkb as wkb
    >>> pt = wkt.loads('POINT EMPTY')
    >>> pt
    {'type': 'Point', 'coordinates': []}
    >>> wkb.dumps(pt)
    Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "/home/jdoe/geomet/geomet/wkb.py", line 216, in dumps
        return _dumps(obj, big_endian)
    File "/home/jdoe/geomet/geomet/wkb.py", line 238, in _dumps
        raise ValueError(
    ValueError: Empty geometries cannot be represented in WKB. Reason: The dimensionality of the WKB would be ambiguous.


## See also

- [wellknown](https://github.com/mapbox/wellknown): A similar package for Node.js.
- [geo](https://github.com/bryanjos/geo): A nearly-identical package for Elixir.
