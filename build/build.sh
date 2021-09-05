#!/bin/bash
set -xeuo pipefail

export PYTHONPATH="${PWD}/packages/python"
export PATH="${PWD}/packages/bash/lib:$PATH"

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

m ci lint -t pycodestyle < <(flake8 packages/python/m)
