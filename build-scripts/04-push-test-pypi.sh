#!/bin/bash

set -euo pipefail

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
ROOT_DIR=${DIR}/..
function cleanup {
    popd > /dev/null
}
pushd ${ROOT_DIR}
trap cleanup EXIT

twine upload --repository-url https://test.pypi.org/legacy/ dist/*
