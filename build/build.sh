#!/bin/bash
set -xeuo pipefail

export PYTHONPATH="${PWD}/packages/python"

# static checks
mypy ./packages/python/m/__main__.py

# tests
./packages/python/tests/run.sh

# pylint
pylint ./packages/python/m --rcfile=.pylintrc

# pep8
pycodestyle --format=pylint packages/python
