#!/bin/bash

set -euxo pipefail

pip install -r test-requirements.txt
# Required for packaging:
pip install setuptools wheel twine readme-renderer==24.0