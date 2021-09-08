#!/bin/bash
set -xeuo pipefail

export PYTHONPATH="${PWD}/packages/python"
export PATH="${PWD}/packages/bash/lib:$PATH"

# Use regex to filter files: --file-regex='.*(npm_tag|http)\.py$'
# m ci lint -t flake8 --prefix-mapping 'packages/python:new/foo' < <(flake8 packages/python/m)

# static checks
mypy ./packages/python/m
mypy ./packages/python/tests

# tests
./packages/python/tests/run.sh

# pylint
pylint ./packages/python/m --rcfile=.pylintrc
pylint ./packages/python/tests --rcfile=packages/python/tests/.pylintrc

# pep8
pycodestyle --format=pylint packages/python
