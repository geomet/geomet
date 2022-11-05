#!/bin/bash

set -euo pipefail

# Specify a tox env/version to run
# If not specified, default to running everything
# Valid versions are py27, py34, py36, etc.
TOX_ENV=${1:-}

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
ROOT_DIR=${DIR}/..
function cleanup {
    popd > /dev/null
}
pushd ${ROOT_DIR}
trap cleanup EXIT

echo "Ensuring that tox is installed..."
which tox || pip install tox

echo "Running tests..."
if [[ "${TOX_ENV}" == "" ]]; then
    tox  # use default envlist
else
    tox -e ${TOX_ENV},style
fi
