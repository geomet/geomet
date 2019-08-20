#!/bin/bash

set -euxo pipefail

twine upload --repository-url https://test.pypi.org/legacy/ dist/*