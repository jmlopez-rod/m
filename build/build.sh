#!/bin/bash
set -xeuo pipefail

export PYTHONPATH="${PWD}/packages/python"
export PATH="${PWD}/packages/bash/lib:$PATH"

# Use regex to filter files: --file-regex='.*(npm_tag|http)\.py$'
# flake8 packages/python/m | m ci celt -t flake8 -m 10

# static checks
mypy ./packages/python/m
mypy ./packages/python/tests

# tests
./packages/python/tests/run.sh

# pylint
m ci celt -t pylint -m 10 -c @allowed_errors.json < <(pylint ./packages/python/m --rcfile=.pylintrc -f json)
pylint ./packages/python/tests --rcfile=packages/python/tests/.pylintrc

# pep8
pycodestyle --format=pylint packages/python
