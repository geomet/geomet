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

"""Simple CLI for converting between WKB/WKT and GeoJSON

Example usage:

  $ echo "POINT (0.9999999 0.9999999)" | python -m geomet.tool --wkb | python -m geomet.tool --wkt --precision 7
  POINT (0.9999999 0.9999999)
"""

import json
import logging
import sys

import click

from geomet import wkb, wkt

def configure_logging(verbosity):
    log_level = max(10, 30 - 10*verbosity)
    logging.basicConfig(stream=sys.stderr, level=log_level)

def transform_geom(g, precision=-1):
    if g['type'] == 'Point':
        x, y = g['coordinates']
        xp, yp = [x], [y]
        if precision >= 0:
            xp = [round(v, precision) for v in xp]
            yp = [round(v, precision) for v in yp]
        new_coords = list(zip(xp, yp))[0]
    if g['type'] in ['LineString', 'MultiPoint']:
        xp, yp = list(*zip(g['coordinates']))
        if precision >= 0:
            xp = [round(v, precision) for v in xp]
            yp = [round(v, precision) for v in yp]
        new_coords = list(zip(xp, yp))
    elif g['type'] in ['Polygon', 'MultiLineString']:
        new_coords = []
        for piece in g['coordinates']:
            xp, yp = list(*zip(*piece))
            if precision >= 0:
                xp = [round(v, precision) for v in xp]
                yp = [round(v, precision) for v in yp]
            new_coords.append(list(zip(xp, yp)))
    elif g['type'] == 'MultiPolygon':
        parts = g['coordinates']
        new_coords = []
        for part in parts:
            inner_coords = []
            for ring in part:
                xp, yp = list(*zip(*ring))
                if precision >= 0:
                    xp = [round(v, precision) for v in xp]
                    yp = [round(v, precision) for v in yp]
                inner_coords.append(list(zip(xp, yp)))
            new_coords.append(inner_coords)
    g['coordinates'] = new_coords
    return g

@click.command(short_help="Convert between WKB/WKT and GeoJSON using stdin and stdout.")
@click.option('--verbose', '-v', count=True, help="Increase verbosity.")
@click.option('--quiet', '-q', count=True, help="Decrease verbosity.")
@click.option('--json', 'output_format', flag_value='json', default=True, 
              help="JSON output.")
@click.option('--wkb', 'output_format', flag_value='wkb',
              help="WKB output.")
@click.option('--wkt', 'output_format', flag_value='wkt',
              help="WKT output.")
@click.option('--precision', type=int, default=-1,
              help="Decimal precision of JSON and WKT coordinates.")
@click.option('--indent', default=None, type=int,
              help="Indentation level for pretty printed output")
def cli(verbose, quiet, output_format, precision, indent):
    verbosity = verbose - quiet
    configure_logging(verbosity)
    logger = logging.getLogger('geomet')

    # Detect the input format
    stdin = click.get_binary_stream('stdin')
    
    try:
        input = stdin.read()
        try:
            text = input.decode('utf-8').strip()
            if text.startswith('{'):
                geom = json.loads(text)
            else:
                geom = wkt.loads(text)
        except UnicodeDecodeError:
            geom = wkb.loads(input)

        if output_format == 'wkb':
            output = wkb.dumps(geom)
        elif output_format == 'wkt':
            kwds = {}
            if precision >= 0:
                kwds['decimals'] = precision
            output = wkt.dumps(geom, **kwds)
        else:
            if precision >= 0:
                geom = transform_geom(geom, precision)
            output = json.dumps(geom, indent=indent)
        logger.debug("Output: %r", output)

        if output_format in ('json', 'wkt'):
            stdout = click.get_text_stream('stdout')
        else:
            stdout = click.get_binary_stream('stdout')
        stdout.write(output)
        stdout.write("\n")
        sys.exit(0)

    except Exception:
        logger.exception("Failed. Exception caught")
        sys.exit(1)

if __name__ == '__main__':
    cli()

