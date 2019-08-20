#!/bin/bash

set -euxo pipefail

# Create soure and binary distributions:
python setup.py sdist bdist_wheel