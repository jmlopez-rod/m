#!/bin/bash
set -xeuo pipefail

m message open 'setup' 'update paths'
export PYTHONPATH="${PWD}/packages/python"

m message sibling_block 'setup' 'lint' 'run flake8 on source code'
# Use regex to filter files: --file-regex='.*(npm_tag|http)\.py$'
m ci celt -t flake8 -c @allowed_errors.json < <(flake8 packages/python/m)
flake8 packages/web/docs

# static checks
m message sibling_block 'lint' 'mypy' 'static checks'
mypy ./packages/python/m
mypy ./packages/python/tests

# tests
m message sibling_block 'mypy' 'tests' 'run all tests'
./packages/python/tests/run.sh

# lint tests
m message sibling_block 'flake8' 'lint-tests' 'run linters on tests'
m ci celt -t flake8 -c @allowed_errors_tests.json < <(flake8 packages/python/tests --config .flake8-tests)
