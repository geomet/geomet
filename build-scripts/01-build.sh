#!/bin/bash

set -euxo pipefail

pip install -r requirements.txt
python setup.py -q install