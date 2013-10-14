import StringIO
import tokenize


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
    geom_type = obj['type']
    exporter = __dumps_registry.get(geom_type)

    if exporter is None:
        __unsupported_geom_type(geom_type)

    fmt = '%%.%df' % decimals
    return exporter(obj, fmt)


def loads(string):
    """
    Construct a GeoJSON `dict` from WKT (`string`).
    """
    sio = StringIO.StringIO(string)
    # NOTE: This is not the intended purpose of `tokenize`, but it works.
    tokens = (x[1] for x in tokenize.generate_tokens(sio.readline))
    tokens = __tokenize_wkt(tokens)
    geom_type = tokens.next()

    importer = __loads_registry.get(geom_type)

    if importer is None:
        __unsupported_geom_type(geom_type)
    return importer(tokens, string)


def __tokenize_wkt(tokens):
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


def __unsupported_geom_type(geom_type):
    raise ValueError("Unsupported geometry type '%s'" % geom_type)


def __dump_point(obj, fmt):
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


def __dump_linestring(obj, fmt):
    """
    Dump a GeoJSON-like LineString object to WKT.

    Input parameters and return value are the LINESTRING equivalent to
    :func:`__dump_point`.
    """
    coords = obj['coordinates']
    ls = 'LINESTRING (%s)'
    ls %= ', '.join(' '.join(fmt % c for c in pt) for pt in coords)
    return ls


def __dump_polygon(obj, fmt):
    """
    Dump a GeoJSON-like Polygon object to WKT.

    Input parameters and return value are the POLYGON equivalent to
    :func:`__dump_point`.
    """
    coords = obj['coordinates']
    poly = 'POLYGON (%s)'
    rings = (', '.join(' '.join(fmt % c for c in pt) for pt in ring)
             for ring in coords)
    rings = ('(%s)' % r for r in rings)
    poly %= ', '.join(rings)
    return poly


def __dump_multipoint(obj, fmt):
    """
    Dump a GeoJSON-like MultiPoint object to WKT.

    Input parameters and return value are the POLYGON equivalent to
    :func:`__dump_point`.
    """
    coords = obj['coordinates']
    mp = 'MULTIPOINT (%s)'
    points = (' '.join(fmt % c for c in pt) for pt in coords)
    # Add parens around each point.
    points = ('(%s)' % pt for pt in points)
    mp %= ', '.join(points)
    return mp


def __dump_multilinestring(obj, fmt):
    raise NotImplementedError


def __dump_multipolygon(obj, fmt):
    raise NotImplementedError


def __dump_geometrycollection(obj, fmt):
    raise NotImplementedError


__dumps_registry = {
    'Point':  __dump_point,
    'LineString': __dump_linestring,
    'Polygon': __dump_polygon,
    'MultiPoint': __dump_multipoint,
    'MultiLineString': __dump_multilinestring,
    'MultiPolygon': __dump_multipolygon,
    'GeometryCollection': __dump_geometrycollection,
}


def __load_point(tokens, string):
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
    if not tokens.next() == '(':
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


def __load_linestring(tokens, string):
    """
    Has similar inputs and return value to to :func:`__load_point`, except is
    for handling LINESTRING geometry.

    :returns:
        A GeoJSON `dict` LineString representation of the WKT ``string``.
    """
    if not tokens.next() == '(':
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


def __load_polygon(tokens, string):
    """
    Has similar inputs and return value to to :func:`__load_point`, except is
    for handling POLYGON geometry.

    :returns:
        A GeoJSON `dict` Polygon representation of the WKT ``string``.
    """
    open_parens = tokens.next(), tokens.next()
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


def __load_multipoint(tokens, string):
    """
    Has similar inputs and return value to to :func:`__load_point`, except is
    for handling MULTIPOINT geometry.

    :returns:
        A GeoJSON `dict` MultiPoint representation of the WKT ``string``.
    """
    open_paren = tokens.next()
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


def __load_multipolygon(tokens, string):
    """
    Has similar inputs and return value to to :func:`__load_point`, except is
    for handling MULTIPOLYGON geometry.

    :returns:
        A GeoJSON `dict` MultiPolygon representation of the WKT ``string``.
    """
    open_paren = tokens.next()
    if not open_paren == '(':
        raise ValueError(INVALID_WKT_FMT % string)

    polygons = []
    while True:
        try:
            poly = __load_polygon(tokens, string)
            polygons.append(poly['coordinates'])
            t = tokens.next()
            if t == ')':
                # we're done; no more polygons.
                break
        except StopIteration:
            # If we reach this, the WKT is not valid.
            raise ValueError(INVALID_WKT_FMT % string)

    return dict(type='MultiPolygon', coordinates=polygons)


def __load_multilinestring(tokens, string):
    """
    Has similar inputs and return value to to :func:`__load_point`, except is
    for handling MULTILINESTRING geometry.

    :returns:
        A GeoJSON `dict` MultiLineString representation of the WKT ``string``.
    """
    open_paren = tokens.next()
    if not open_paren == '(':
        raise ValueError(INVALID_WKT_FMT % string)

    linestrs = []
    while True:
        try:
            linestr = __load_linestring(tokens, string)
            linestrs.append(linestr['coordinates'])
            t = tokens.next()
            if t == ')':
                # we're done; no more linestrings.
                break
        except StopIteration:
            # If we reach this, the WKT is not valid.
            raise ValueError(INVALID_WKT_FMT % string)

    return dict(type='MultiLineString', coordinates=linestrs)


def __load_geometrycollection(tokens, string):
    raise NotImplementedError


__loads_registry = {
    'POINT': __load_point,
    'LINESTRING': __load_linestring,
    'POLYGON': __load_polygon,
    'MULTIPOINT': __load_multipoint,
    'MULTILINESTRING': __load_multilinestring,
    'MULTIPOLYGON': __load_multipolygon,
    'GEOMETRYCOLLECTION': __load_geometrycollection,
}
