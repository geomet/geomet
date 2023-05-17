#!/bin/bash

set -euo pipefail

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
ROOT_DIR=${DIR}/..
function cleanup {
    popd > /dev/null
}
pushd ${ROOT_DIR}
trap cleanup EXIT

# Clean any previous builds:
rm -rfv geomet.egg-info
rm -rfv dist

# Create source and binary distributions:
python -m build

# Check the package for publishing suitability:
twine check --strict dist/*
