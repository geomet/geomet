"""
GeoMet

Convert GeoJSON to WKT/WKB (Well-Known Text/Binary), and vice versa.
"""

import re
import sys

from setuptools import find_packages
from setuptools import setup

if (3,2) < sys.version_info < (3,4):
    raise RuntimeError("Python3.3 is no longer supported")


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
    description='GeoJSON <-> WKT/WKB conversion utilities',
    long_description=__doc__,
    platforms=['any'],
    packages=find_packages(exclude=['geomet.tests', 'geomet.tests.*']),
    entry_points={'console_scripts': ['geomet=geomet.tool:cli']},
    license='Apache 2.0',
    keywords='wkb wkt geojson',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: GIS',
    ],
    zip_safe=False,
    install_requires=['click', 'six'],
    python_requires=">2.6, !=3.3.*, <4",
)
