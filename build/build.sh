#!/bin/bash
set -xeuo pipefail

export PYTHONPATH="${PWD}/src"

# static checks
mypy ./src/m/__main__.py

# tests
./src/tests/run.sh

# pylint
pylint m --rcfile=.pylintrc

# pep8
pycodestyle --format=pylint src
