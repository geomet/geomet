This document explains in the detail the WKB geometry structure and includes exampes of each major type of geometry. WKB is in hexadecimal notation.

### Point ###

- 1 byte int: endianness
- 4 byte int: geometry type (2d, 3d, or 4d)
- Series of N 8 byte floats: coordinate values (where N is the number of dimensions)

Example:

    POINT(1.0 0.0)
    00 00000001 3ff0000000000000 0000000000000000  (big endian)
    01 01000000 0000000000000000 000000000000f03f  (little endian)


### LineString ###

- 1 byte int: endianness
- 4 byte int: geometry type (2d, 3d, or 4d)
- 4 byte int: number of vertices in linestring
- Series of N*M 8 byte floats: coordinate values (where N is the number of dimensions and M is the number of vertices)

Example:

    LINESTRING(-100.0 0.0, -101.0 -1.0)
    00 00000002 00000002 c059000000000000 0000000000000000 c059400000000000 bff0000000000000

### Polygon ###

- 1 byte int: endianness
- 4 byte int: geometry type (2d, 3d, or 4d)
- 4 byte int: number of rings
- Series of >= 1 rings, where each is:
    - 4 byte int: number of vertices in ring
    - Series of N*M 8 byte floats: coordinate values (where N is the number of dimensions and M is the number of vertices)

Example:

    POLYGON ((100.0010 0.0010, 101.1235 0.0010, 101.0010 1.0010, 100.0010 0.0010), (100.2010 0.2010, 100.8010 0.2010, 100.8010 0.8010, 100.2010 0.2010))
    00 00000003 00000002  # header, with number of rings
        00000004  # number of verts in ring
            40590010624dd2f2 3f50624dd2f1a9fc
            405947e76c8b4396 3f50624dd2f1a9fc
            40594010624dd2f2 3ff004189374bc6a
            40590010624dd2f2 3f50624dd2f1a9fc
        00000004 # number of verts in ring
            40590cdd2f1a9fbe 3fc9ba5e353f7cee
            4059334395810625 3fc9ba5e353f7cee
            4059334395810625 3fe9a1cac083126f
            40590cdd2f1a9fbe 3fc9ba5e353f7cee

### MultiPoint ###

- 1 byte int: endianness
- 4 byte int: geometry type (2d, 3d, or 4d)
- 4 byte int: number of points
- Series of Point geometries, including endianness header (see above)

Example:

    MULTIPOINT((0.0 0.0),(1.0 1.0))
    00 00000004 00000002
        00 00000001 0000000000000000 0000000000000000
        00 00000001 3ff0000000000000 3ff0000000000000
    01 04000000 02000000
        01 01000000 0000000000000000 0000000000000000
        01 01000000 000000000000f03f 000000000000f03f
    MULTIPOINT((1.0 1.0),(1.0 1.0))
    00 00000004 00000002
        00 00000001 3ff0000000000000 3ff0000000000000
        00 00000001 3ff0000000000000 3ff0000000000000
    MULTIPOINT((1.0 1.0 1.0),(1.0 1.0 1.0))
    00 000003ec 00000002
        00 000003e9 3ff0000000000000 3ff0000000000000 3ff0000000000000
        00 000003e9 3ff0000000000000 3ff0000000000000 3ff0000000000000

### MultiLineString ###

- 1 byte int: endianness
- 4 byte int: geometry type (2d, 3d, or 4d)
- 4 byte int: number of linestrings
- Series LineString geometries, including endianness header (see above)

Example:

    MULTILINESTRING ((0 -1, -2 -3, -4 -5), (1.66 -31023.5, 10000.9999 2.2, 100.9 3.3, 0 4.4))
    00 00000005 00000002
        00 00000002 00000003 0000000000000000 bff0000000000000 c000000000000000 c008000000000000 c010000000000000 c014000000000000
        00 00000002 00000004 3ffa8f5c28f5c28f c0de4be000000000 40c3887ffcb923a3 400199999999999a 405939999999999a 400a666666666666 0000000000000000 401199999999999a
    01 05000000 02000000
        01 02000000 03000000 0000000000000000 000000000000f0bf 00000000000000c0 00000000000008c0 00000000000010c0 00000000000014c0
        01 02000000 04000000 8fc2f5285c8ffa3f 00000000e04bdec0 a323b9fc7f88c340 9a99999999990140 9a99999999395940 6666666666660a40 0000000000000000 9a99999999991140

### MultiPolygon ###

- 1 byte int: endianness
- 4 byte int: geometry type
- 4 byte int: number of polygons
- Series of Polygon geometries, including endianness header (see above)

Example:

    MULTIPOLYGON (((100.001 0.001, 101.001 0.001, 101.001 1.001, 100.001 0.001), (100.201 0.201, 100.801 0.201, 100.801 0.801, 100.201 0.201)), ((1 2, 5 6, 9 10, 1 2)))
    00 00000006 00000002  # multipolygon header
        00 00000003 00000002  # polygon header
            00000004 40590010624dd2f2 3f50624dd2f1a9fc 40594010624dd2f2 3f50624dd2f1a9fc 40594010624dd2f2 3ff004189374bc6a 40590010624dd2f2 3f50624dd2f1a9fc
            00000004 40590cdd2f1a9fbe 3fc9ba5e353f7cee 4059334395810625 3fc9ba5e353f7cee 4059334395810625 3fe9a1cac083126f 40590cdd2f1a9fbe 3fc9ba5e353f7cee
        00 00000003 00000001  # polygon header
            00000004 3ff0000000000000 4000000000000000 4014000000000000 4018000000000000 4022000000000000 4024000000000000 3ff0000000000000 4000000000000000

### GeometryCollection ###

- 1 byte int: endianness
- 4 byte int: geometry type
- bytes of the contained geometries

Example:

    GEOMETRYCOLLECTION(POINT(0.0 0.0),LINESTRING(1.0 1.0, 2.0 2.0))
    00 00000007 00000002
        00 00000001  # point header
            0000000000000000 0000000000000000
        00 00000002 00000002  # linestring header
            3ff0000000000000 3ff0000000000000 4000000000000000 4000000000000000
