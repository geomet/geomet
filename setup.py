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
    url='https://github.com/larsbutler/geomet',
    description='GeoJSON <-> WKT/WKB conversion utilities',
    long_description=__doc__,
    platforms=['any'],
    packages=find_packages(exclude=['geomet.tests', 'geomet.tests.*']),
    scripts=['scripts/geomet'],
    provides=['geomet (%s)' % VERSION],
    license='BSD',
    keywords='wkb wkt geojson',
    classifiers=(
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Topic :: Scientific/Engineering :: GIS',
    ),
    zip_safe=False,
    install_requires=['click', 'six'],
)
