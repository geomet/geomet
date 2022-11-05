#!/bin/bash

set -euo pipefail

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
ROOT_DIR=${DIR}/..
function cleanup {
    popd > /dev/null
}
pushd ${ROOT_DIR}
trap cleanup EXIT

# Create source and binary distributions:
python setup.py sdist bdist_wheel