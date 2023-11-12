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
import json
import geomet


def load(source_file):
    """
    Converts Esri Json File to GeoJSON.

    :param source_file:
        Path to a file that contains the Esri JSON data.

    :returns:
         A GeoJSON `dict` representing the geometry read from the file.

    """
    return json.load(source_file)


def loads(string):
    """
    Construct a GeoJSON `dict` from Esri JSON (string/dict).

    :param string:
        The Esri JSON geometry representation

    :returns:
         A GeoJSON `dict` representing the geometry read from the file.
    """
    data = json.loads(string)

    if "rings" in data:
        return _esri_to_geojson_convert["rings"](data)
    elif "paths" in data:
        return _esri_to_geojson_convert["paths"](data)
    elif "x" in data or "y" in data:
        return _esri_to_geojson_convert["x"](data)
    elif "points" in data:
        return _esri_to_geojson_convert["points"](data)
    else:
        raise geomet.InvalidGeoJSONException("Invalid EsriJSON: %s" % string)


def dump(obj, dest_file, srid=None):
    """
    Converts GeoJSON to Esri JSON File.
    """
    return json.dump(dumps(obj, srid=srid), dest_file)


def dumps(obj, srid=None):
    """
    Dump a GeoJSON-like `dict` to a Esri JSON.

    :param string:
        The GeoJSON geometry representation
    :param int:
        The default SRID value if none is present.

    """
    if "type" in obj and obj["type"].lower() in _gj_to_esri.keys():
        convert = _gj_to_esri[obj["type"].lower()]
        return convert(obj, srid=srid)
    else:
        raise geomet.InvalidGeoJSONException("Invalid GeoJSON type %s" % obj)


def _extract_geojson_srid(obj):
    """
    Extracts the SRID code (WKID code) from geojson. If not found, SRID=4326

    :returns: Integer
    """
    meta_srid = obj.get("meta", {}).get("srid", None)
    # Also try to get it from `crs.properties.name`:
    crs_srid = obj.get("crs", {}).get("properties", {}).get("name", None)
    if crs_srid is not None:
        # Shave off the EPSG: prefix to give us the SRID:
        crs_srid = crs_srid.replace("EPSG:", "")

    if (
        meta_srid is not None
        and crs_srid is not None
        and str(meta_srid) != str(crs_srid)
    ):
        raise ValueError(
            "Ambiguous CRS/SRID values: %s and %s" % (meta_srid, crs_srid)
        )
    srid = meta_srid or crs_srid

    return srid or 4326


def _dump_geojson_point(obj, srid=None):
    """
    Loads GeoJSON to Esri JSON for Geometry type Point.


    """
    coordkey = "coordinates"
    coords = obj[coordkey]
    if srid is None:
        srid = _extract_geojson_srid(obj)
    return {"x": coords[0], "y": coords[1], "spatialReference": {"wkid": srid}}


def _dump_geojson_multipoint(obj, srid=None):
    """
    Loads GeoJSON to Esri JSON for Geometry type MultiPoint.

    """
    coordkey = "coordinates"
    if srid is None:
        srid = _extract_geojson_srid(obj)
    return {"points": obj[coordkey], "spatialReference": {"wkid": srid}}


def _dump_geojson_polyline(obj, srid=None):
    """
    Loads GeoJSON to Esri JSON for Geometry type LineString and
    MultiLineString.

    """
    coordkey = "coordinates"
    if obj["type"].lower() == "linestring":
        coordinates = [obj[coordkey]]
    else:
        coordinates = obj[coordkey]
    if srid is None:
        srid = _extract_geojson_srid(obj)
    return {"paths": coordinates, "spatialReference": {"wkid": srid}}


def _dump_geojson_polygon(data, srid=None):
    """
    Loads GeoJSON to Esri JSON for Geometry type Polygon or MultiPolygon.

    """
    coordkey = "coordinates"
    coordinates = data[coordkey]
    typekey = ([d for d in data if d.lower() == "type"] or ["type"]).pop()
    if data[typekey].lower() == "polygon":
        coordinates = [coordinates]
    part_list = []
    for part in coordinates:
        if len(part) == 1:
            part_list.append(part[0])
        else:
            for seg in part:
                part_list.append([list(coord) for coord in seg])
    if srid is None:
        srid = _extract_geojson_srid(data)
    return {"rings": part_list, "spatialReference": {"wkid": srid}}


def _to_gj_point(obj):
    """
    Dump a Esri JSON Point to GeoJSON Point.

    :param dict obj:
        A EsriJSON-like `dict` representing a Point.


    :returns:
        GeoJSON representation of the Esri JSON Point
    """
    if obj.get("x", None) is None or obj.get("y", None) is None:
        return {"type": "Point", "coordinates": ()}
    return {"type": "Point", "coordinates": (obj.get("x"), obj.get("y"))}


def _to_gj_polygon(obj):
    """
    Dump a EsriJSON-like Polygon object to GeoJSON.

    Input parameters and return value are the POLYGON equivalent to
    :func:`_to_gj_point`.
    """

    def split_part(a_part):
        part_list = []
        for item in a_part:
            if item is None:
                if part_list:
                    yield part_list
                part_list = []
            else:
                part_list.append((item[0], item[1]))
        if part_list:
            yield part_list

    part_json = [list(split_part(part)) for part in obj["rings"]]
    return {"type": "MultiPolygon", "coordinates": part_json}


def _to_gj_multipoint(data):
    """
    Dump a EsriJSON-like MultiPoint object to GeoJSON-dict.

    Input parameters and return value are the MULTIPOINT equivalent to
    :func:`_to_gj_point`.

    :returns: `dict`
    """

    return {"type": "MultiPoint", "coordinates": [pt for pt in data["points"]]}


def _to_gj_polyline(data):
    """
    Dump a GeoJSON-like MultiLineString object to WKT.

    Input parameters and return value are the MULTILINESTRING equivalent to
    :func:`_dump_point`.
    """
    return {
        "type": "MultiLineString",
        "coordinates": [
            [((pt[0], pt[1]) if pt else None) for pt in part]
            for part in data["paths"]
        ],
    }


_esri_to_geojson_convert = {
    "x": _to_gj_point,
    "y": _to_gj_point,
    "points": _to_gj_multipoint,
    "rings": _to_gj_polygon,
    "paths": _to_gj_polyline,
}

_gj_to_esri = {
    "point": _dump_geojson_point,
    "multipoint": _dump_geojson_multipoint,
    "linestring": _dump_geojson_polyline,
    "multilinestring": _dump_geojson_polyline,
    "polygon": _dump_geojson_polygon,
    "multipolygon": _dump_geojson_polygon,
}
