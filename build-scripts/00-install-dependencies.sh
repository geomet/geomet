#!/bin/bash

set -euxo pipefail

# Install depenencies for build/test/package steps:
pip install -r test-requirements.txt -r packaging-requirements.txt