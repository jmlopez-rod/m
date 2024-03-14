#!/bin/bash
set -xeuo pipefail

# flake8
m message sibling_block 'tests' 'flake8' 'run flake8 on src code'
m ci celt -t flake8 -c @allowed_errors.json < <(flake8 packages/python/m)
# lint tests

m message sibling_block 'flake8' 'lint-tests' 'run linters on tests'
m ci celt -t flake8 -c @allowed_errors_tests.json < <(flake8 packages/python/tests --config .flake8-tests)
