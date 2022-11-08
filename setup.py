"""
GeoMet

Convert GeoJSON to WKT/WKB (Well-Known Text/Binary), and vice versa.
"""

import re
import sys

from setuptools import find_packages
from setuptools import setup


def get_version():
    version_re = r"^__version__\s+=\s+['\"]([^'\"]*)['\"]"
    version = None

    for line in open('geomet/__init__.py', 'r'):
        version_match = re.search(version_re, line, re.M)
        if version_match:
            version = version_match.group(1)
            break
    else:
        sys.exit('__version__ variable not found in geomet/__init__.py')

    return version

VERSION = get_version()

setup(
    name='geomet',
    version=VERSION,
    maintainer='Lars Butler',
    maintainer_email='lars.butler@gmail.com',
    url='https://github.com/geomet/geomet',
    description='Conversion library for common geospatial data formats (GeoJSON/WKT/EWKT/WKB/EWKB/GeoPackage/EsriJson)',
    long_description=__doc__,
    platforms=['any'],
    packages=find_packages(exclude=['geomet.tests', 'geomet.tests.*']),
    entry_points={'console_scripts': ['geomet=geomet.tool:cli']},
    license='Apache 2.0',
    keywords=[
        'esri',
        'ewkb',
        'ewkt',
        'geojson',
        'geopackage',
        'geospatial',
        'gis',
        'spatial',
        'wkb',
        'wkt',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: GIS',
    ],
    zip_safe=False,
    install_requires=['click', 'six'],
    python_requires=">=3.7, <4",
)
