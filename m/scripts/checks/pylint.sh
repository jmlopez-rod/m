#!/bin/bash
set -xeuo pipefail

# pylint
m message sibling_block 'tests' 'pylint' 'run pylint on src code'
m ci celt -t pylint -m 10 -c @allowed_errors.json < <(pylint ./packages/python/m --rcfile=.pylintrc -f json)

# lint tests
m message sibling_block 'pylint' 'lint-tests' 'run linters on tests'
m ci celt -t flake8 -c @allowed_errors_tests.json < <(flake8 packages/python/tests --config .flake8-tests)
m ci celt -t pylint -m 10 -c @allowed_errors_tests.json < <(pylint ./packages/python/tests --rcfile=packages/python/tests/.pylintrc -f json)
