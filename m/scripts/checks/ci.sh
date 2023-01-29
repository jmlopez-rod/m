#!/bin/bash
set -xeuo pipefail

export PYTHONPATH="${PWD}/packages/python"
export PATH="${PWD}/packages/bash/lib:$PATH"

# Use regex to filter files: --file-regex='.*(npm_tag|http)\.py$'
m ci celt -m 15 -t flake8 -c @allowed_errors.json < <(flake8 packages/python/m)

# static checks
mypy ./packages/python/m
mypy ./packages/python/tests

# tests
./packages/python/tests/run.sh
# Can't run these in ci due to environment variables
# (
# cd packages/bash/tests && ./run.sh
# )

# pylint
m ci celt -t pylint -m 10 -c @allowed_errors.json < <(pylint ./packages/python/m --rcfile=.pylintrc -f json)

# need to update celt to get these issues in the allowed_errors.json file
# pylint ./packages/python/tests --rcfile=packages/python/tests/.pylintrc

# pep8
pycodestyle --format=pylint packages/python
