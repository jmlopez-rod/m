#!/bin/bash
set -euo pipefail

export DEBUG_HTTP_INCLUDE_BODY=1

SINGLE=true
# SINGLE=false

# Make sure we run all test in the pipelines
if [ "${CI:-false}" = 'true' ]; then
  SINGLE=false
fi

if [ "$SINGLE" = 'false' ]; then
  coverage run --source packages/python/m -m pytest -p no:logging
  coverage report -m --fail-under 98
else
  # To run specific tests:
  source="packages/python/m/github/actions"
  filter="test_blueprints"
  coverage run --source "$source" -m pytest -p no:logging packages/python -vv -k "$filter"
  coverage report -m
fi

mkdir -p m/.m
touch m/.m/pytest-ran
