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
import geomet
import itertools
import six
import tokenize

try:
    import StringIO
except ImportError:
    import io
    StringIO = io

from geomet import util


INVALID_WKT_FMT = 'Invalid WKT: `%s`'


def dump(obj, dest_file):
    """
    Dump GeoJSON-like `dict` to WKT and write it to the `dest_file`.

    :param dict obj:
        A GeoJSON-like dictionary. It must at least the keys 'type' and
        'coordinates'.
    :param dest_file:
        Open and writable file-like object.
    """
    dest_file.write(dumps(obj))


def load(source_file):
    """
    Load a GeoJSON `dict` object from a ``source_file`` containing WKT.

    :param source_file:
        Open and readable file-like object.

    :returns:
        A GeoJSON `dict` representing the geometry read from the file.
    """
    return loads(source_file.read())


def dumps(obj, decimals=16):
    """
    Dump a GeoJSON-like `dict` to a WKT string.
    """
    try:
        geom_type = obj['type']
        exporter = _dumps_registry.get(geom_type)

        if exporter is None:
            _unsupported_geom_type(geom_type)

        # Check for empty cases
        if geom_type == 'GeometryCollection':
            if len(obj['geometries']) == 0:
                return 'GEOMETRYCOLLECTION EMPTY'
        else:
            # Geom has no coordinate values at all, and must be empty.
            if len(list(util.flatten_multi_dim(obj['coordinates']))) == 0:
                return '%s EMPTY' % geom_type.upper()
    except KeyError:
        raise geomet.InvalidGeoJSONException('Invalid GeoJSON: %s' % obj)

    fmt = '%%.%df' % decimals
    return exporter(obj, fmt)


def loads(string):
    """
    Construct a GeoJSON `dict` from WKT (`string`).
    """
    sio = StringIO.StringIO(string)
    # NOTE: This is not the intended purpose of `tokenize`, but it works.
    tokens = (x[1] for x in tokenize.generate_tokens(sio.readline))
    tokens = _tokenize_wkt(tokens)
    geom_type = next(tokens)

    importer = _loads_registry.get(geom_type)

    if importer is None:
        _unsupported_geom_type(geom_type)

    peek = six.advance_iterator(tokens)
    if peek == 'EMPTY':
        if geom_type == 'GEOMETRYCOLLECTION':
            return dict(type='GeometryCollection', geometries=[])
        else:
            return dict(type=_type_map_caps_to_mixed[geom_type],
                        coordinates=[])

    # Put the peeked element back on the head of the token generator
    tokens = itertools.chain([peek], tokens)
    return importer(tokens, string)


def _tokenize_wkt(tokens):
    """
    Since the tokenizer treats "-" and numeric strings as separate values,
    combine them and yield them as a single token. This utility encapsulates
    parsing of negative numeric values from WKT can be used generically in all
    parsers.
    """
    negative = False
    for t in tokens:
        if t == '-':
            negative = True
            continue
        else:
            if negative:
                yield '-%s' % t
            else:
                yield t
            negative = False


def _unsupported_geom_type(geom_type):
    raise ValueError("Unsupported geometry type '%s'" % geom_type)


def _dump_point(obj, fmt):
    """
    Dump a GeoJSON-like Point object to WKT.

    :param dict obj:
        A GeoJSON-like `dict` representing a Point.
    :param str fmt:
        Format string which indicates the number of digits to display after the
        decimal point when formatting coordinates.

    :returns:
        WKT representation of the input GeoJSON Point ``obj``.
    """
    coords = obj['coordinates']
    pt = 'POINT (%s)' % ' '.join(fmt % c for c in coords)
    return pt


def _dump_linestring(obj, fmt):
    """
    Dump a GeoJSON-like LineString object to WKT.

    Input parameters and return value are the LINESTRING equivalent to
    :func:`_dump_point`.
    """
    coords = obj['coordinates']
    ls = 'LINESTRING (%s)'
    ls %= ', '.join(' '.join(fmt % c for c in pt) for pt in coords)
    return ls


def _dump_polygon(obj, fmt):
    """
    Dump a GeoJSON-like Polygon object to WKT.

    Input parameters and return value are the POLYGON equivalent to
    :func:`_dump_point`.
    """
    coords = obj['coordinates']
    poly = 'POLYGON (%s)'
    rings = (', '.join(' '.join(fmt % c for c in pt) for pt in ring)
             for ring in coords)
    rings = ('(%s)' % r for r in rings)
    poly %= ', '.join(rings)
    return poly


def _dump_multipoint(obj, fmt):
    """
    Dump a GeoJSON-like MultiPoint object to WKT.

    Input parameters and return value are the MULTIPOINT equivalent to
    :func:`_dump_point`.
    """
    coords = obj['coordinates']
    mp = 'MULTIPOINT (%s)'
    points = (' '.join(fmt % c for c in pt) for pt in coords)
    # Add parens around each point.
    points = ('(%s)' % pt for pt in points)
    mp %= ', '.join(points)
    return mp


def _dump_multilinestring(obj, fmt):
    """
    Dump a GeoJSON-like MultiLineString object to WKT.

    Input parameters and return value are the MULTILINESTRING equivalent to
    :func:`_dump_point`.
    """
    coords = obj['coordinates']
    mlls = 'MULTILINESTRING (%s)'
    linestrs = ('(%s)' % ', '.join(' '.join(fmt % c for c in pt)
                for pt in linestr) for linestr in coords)
    mlls %= ', '.join(ls for ls in linestrs)
    return mlls


def _dump_multipolygon(obj, fmt):
    """
    Dump a GeoJSON-like MultiPolygon object to WKT.

    Input parameters and return value are the MULTIPOLYGON equivalent to
    :func:`_dump_point`.
    """
    coords = obj['coordinates']
    mp = 'MULTIPOLYGON (%s)'

    polys = (
        # join the polygons in the multipolygon
        ', '.join(
            # join the rings in a polygon,
            # and wrap in parens
            '(%s)' % ', '.join(
                # join the points in a ring,
                # and wrap in parens
                '(%s)' % ', '.join(
                    # join coordinate values of a vertex
                    ' '.join(fmt % c for c in pt)
                    for pt in ring)
                for ring in poly)
            for poly in coords)
    )
    mp %= polys
    return mp


def _dump_geometrycollection(obj, fmt):
    """
    Dump a GeoJSON-like GeometryCollection object to WKT.

    Input parameters and return value are the GEOMETRYCOLLECTION equivalent to
    :func:`_dump_point`.

    The WKT conversions for each geometry in the collection are delegated to
    their respective functions.
    """
    gc = 'GEOMETRYCOLLECTION (%s)'
    geoms = obj['geometries']
    geoms_wkt = []
    for geom in geoms:
        geom_type = geom['type']
        geoms_wkt.append(_dumps_registry.get(geom_type)(geom, fmt))
    gc %= ','.join(geoms_wkt)
    return gc


def _load_point(tokens, string):
    """
    :param tokens:
        A generator of string tokens for the input WKT, begining just after the
        geometry type. The geometry type is consumed before we get to here. For
        example, if :func:`loads` is called with the input 'POINT(0.0 1.0)',
        ``tokens`` would generate the following values:

        .. code-block:: python
            ['(', '0.0', '1.0', ')']
    :param str string:
        The original WKT string.

    :returns:
        A GeoJSON `dict` Point representation of the WKT ``string``.
    """
    if not next(tokens) == '(':
        raise ValueError(INVALID_WKT_FMT % string)

    coords = []
    try:
        for t in tokens:
            if t == ')':
                break
            else:
                coords.append(float(t))
    except tokenize.TokenError:
        raise ValueError(INVALID_WKT_FMT % string)

    return dict(type='Point', coordinates=coords)


def _load_linestring(tokens, string):
    """
    Has similar inputs and return value to to :func:`_load_point`, except is
    for handling LINESTRING geometry.

    :returns:
        A GeoJSON `dict` LineString representation of the WKT ``string``.
    """
    if not next(tokens) == '(':
        raise ValueError(INVALID_WKT_FMT % string)

    # a list of lists
    # each member list represents a point
    coords = []
    try:
        pt = []
        for t in tokens:
            if t == ')':
                coords.append(pt)
                break
            elif t == ',':
                # it's the end of the point
                coords.append(pt)
                pt = []
            else:
                pt.append(float(t))
    except tokenize.TokenError:
        raise ValueError(INVALID_WKT_FMT % string)

    return dict(type='LineString', coordinates=coords)


def _load_polygon(tokens, string):
    """
    Has similar inputs and return value to to :func:`_load_point`, except is
    for handling POLYGON geometry.

    :returns:
        A GeoJSON `dict` Polygon representation of the WKT ``string``.
    """
    open_parens = next(tokens), next(tokens)
    if not open_parens == ('(', '('):
        raise ValueError(INVALID_WKT_FMT % string)

    # coords contains a list of rings
    # each ring contains a list of points
    # each point is a list of 2-4 values
    coords = []

    ring = []
    on_ring = True
    try:
        pt = []
        for t in tokens:
            if t == ')' and on_ring:
                # The ring is finished
                ring.append(pt)
                coords.append(ring)
                on_ring = False
            elif t == ')' and not on_ring:
                # it's the end of the polygon
                break
            elif t == '(':
                # it's a new ring
                ring = []
                pt = []
                on_ring = True
            elif t == ',' and on_ring:
                # it's the end of a point
                ring.append(pt)
                pt = []
            elif t == ',' and not on_ring:
                # there's another ring.
                # do nothing
                pass
            else:
                pt.append(float(t))
    except tokenize.TokenError:
        raise ValueError(INVALID_WKT_FMT % string)

    return dict(type='Polygon', coordinates=coords)


def _load_multipoint(tokens, string):
    """
    Has similar inputs and return value to to :func:`_load_point`, except is
    for handling MULTIPOINT geometry.

    :returns:
        A GeoJSON `dict` MultiPoint representation of the WKT ``string``.
    """
    open_paren = next(tokens)
    if not open_paren == '(':
        raise ValueError(INVALID_WKT_FMT % string)

    coords = []
    pt = []

    paren_depth = 1
    try:
        for t in tokens:
            if t == '(':
                paren_depth += 1
            elif t == ')':
                paren_depth -= 1
                if paren_depth == 0:
                    break
            elif t == '':
                pass
            elif t == ',':
                # the point is done
                coords.append(pt)
                pt = []
            else:
                pt.append(float(t))
    except tokenize.TokenError:
        raise ValueError(INVALID_WKT_FMT % string)

    # Given the way we're parsing, we'll probably have to deal with the last
    # point after the loop
    if len(pt) > 0:
        coords.append(pt)

    return dict(type='MultiPoint', coordinates=coords)


def _load_multipolygon(tokens, string):
    """
    Has similar inputs and return value to to :func:`_load_point`, except is
    for handling MULTIPOLYGON geometry.

    :returns:
        A GeoJSON `dict` MultiPolygon representation of the WKT ``string``.
    """
    open_paren = next(tokens)
    if not open_paren == '(':
        raise ValueError(INVALID_WKT_FMT % string)

    polygons = []
    while True:
        try:
            poly = _load_polygon(tokens, string)
            polygons.append(poly['coordinates'])
            t = next(tokens)
            if t == ')':
                # we're done; no more polygons.
                break
        except StopIteration:
            # If we reach this, the WKT is not valid.
            raise ValueError(INVALID_WKT_FMT % string)

    return dict(type='MultiPolygon', coordinates=polygons)


def _load_multilinestring(tokens, string):
    """
    Has similar inputs and return value to to :func:`_load_point`, except is
    for handling MULTILINESTRING geometry.

    :returns:
        A GeoJSON `dict` MultiLineString representation of the WKT ``string``.
    """
    open_paren = next(tokens)
    if not open_paren == '(':
        raise ValueError(INVALID_WKT_FMT % string)

    linestrs = []
    while True:
        try:
            linestr = _load_linestring(tokens, string)
            linestrs.append(linestr['coordinates'])
            t = next(tokens)
            if t == ')':
                # we're done; no more linestrings.
                break
        except StopIteration:
            # If we reach this, the WKT is not valid.
            raise ValueError(INVALID_WKT_FMT % string)

    return dict(type='MultiLineString', coordinates=linestrs)


def _load_geometrycollection(tokens, string):
    """
    Has similar inputs and return value to to :func:`_load_point`, except is
    for handling GEOMETRYCOLLECTIONs.

    Delegates parsing to the parsers for the individual geometry types.

    :returns:
        A GeoJSON `dict` GeometryCollection representation of the WKT
        ``string``.
    """
    open_paren = next(tokens)
    if not open_paren == '(':
        raise ValueError(INVALID_WKT_FMT % string)

    geoms = []
    result = dict(type='GeometryCollection', geometries=geoms)
    while True:
        try:
            t = next(tokens)
            if t == ')':
                break
            elif t == ',':
                # another geometry still
                continue
            else:
                geom_type = t
                load_func = _loads_registry.get(geom_type)
                geom = load_func(tokens, string)
                geoms.append(geom)
        except StopIteration:
            raise ValueError(INVALID_WKT_FMT % string)
    return result


_dumps_registry = {
    'Point':  _dump_point,
    'LineString': _dump_linestring,
    'Polygon': _dump_polygon,
    'MultiPoint': _dump_multipoint,
    'MultiLineString': _dump_multilinestring,
    'MultiPolygon': _dump_multipolygon,
    'GeometryCollection': _dump_geometrycollection,
}


_loads_registry = {
    'POINT': _load_point,
    'LINESTRING': _load_linestring,
    'POLYGON': _load_polygon,
    'MULTIPOINT': _load_multipoint,
    'MULTILINESTRING': _load_multilinestring,
    'MULTIPOLYGON': _load_multipolygon,
    'GEOMETRYCOLLECTION': _load_geometrycollection,
}

_type_map_caps_to_mixed = dict(
    POINT='Point',
    LINESTRING='LineString',
    POLYGON='Polygon',
    MULTIPOINT='MultiPoint',
    MULTILINESTRING='MultiLineString',
    MULTIPOLYGON='MultiPolygon',
    GEOMETRYCOLLECTION='GeometryCollection',
)
