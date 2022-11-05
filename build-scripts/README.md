# Build scripts

This directory contains build scripts intended to be run inside a CI/CD
environment. The numeric prefix on each file name indicates the order in which
each script should be run in order to set up the build environment, build
packages, run tests, and push packages to PyPI.

It's assumed that Python is available in the test environment. Tests are run
for a single Python version at a time, due to the complexity involved in having
all supported Python versions in a single build environment.