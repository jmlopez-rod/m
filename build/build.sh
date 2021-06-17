#!/bin/bash
set -xeuo pipefail

export PYTHONPATH="${PWD}/src"

# tests
./src/tests/run.sh

# static checks
mypy ./src/m/__main__.py

# pylint
pylint m --rcfile=.pylintrc

# pep8
pycodestyle --format=pylint src
