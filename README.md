geomet
======

GeoMet - Convert GeoJSON to [WKT/WKB](http://en.wikipedia.org/wiki/Well-known_text), and vice versa

The name "GeoMet" comes from "met", the German word for [mead](http://en.wikipedia.org/wiki/Mead).
It is also a shortened version of the word "geometry".

### Example usage ###

Coverting a 'Point' GeoJSON object to WKT:

    >>> from geomet import wkt
    >>> point = {'type': 'Point', 'coordinates': [116.4, 45.2, 11.1]}
    >>> wkt.dumps(point, decimals=4)
    'POINT(116.4000 45.2000 11.1000)'

Converting a 'LineString' GeoJSON object to WKT:

    >>> linestring = {'type':'LineString', 'coordinates': [[0.0, 0.0, 10.0], [2.0, 1.0, 20.0], [4.0, 2.0, 30.0], [5.0, 4.0, 40.0]]}
    >>> wkt.dumps(linestring, decimals=3)
    'LINESTRING(0.000 0.000 10.000, 2.000 1.000 20.000, 4.000 2.000 30.000, 5.000 4.000 40.000)'
