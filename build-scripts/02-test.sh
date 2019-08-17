#!/bin/bash

set -euxo pipefail

echo "Running tests..."
nosetests --with-doctest --with-coverage --cover-package=geomet

# if [ "${TRAVIS:-}" = "true" ]; then
#     echo "Running tests in Travis-CI environment..."
#     export PY_TEST_VERSION=py$(echo ${TRAVIS_PYTHON_VERSION} | sed '/\.//')
#     tox -e style,${PY_TEST_VERSION}
# else
#     echo "Running tests..."
#     tox
# fi
