#!/bin/bash

set -euxo pipefail

pip install -r requirements.txt
python setup.py -q install
# Verify that the `geomet` CLI was installed:
which geomet