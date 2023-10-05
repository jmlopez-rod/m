#!/bin/bash
set -euo pipefail

export DEBUG_HTTP_INCLUDE_BODY=1

SINGLE=true
# SINGLE=false

if [ "$SINGLE" = 'false' ]; then
  coverage run --source packages/python/m -m pytest -p no:logging
  coverage report -m --fail-under 98
else
  # To run specific tests:
  source="packages/python/m/github/actions"
  filter="test_m_gh_actions"
  coverage run --source "$source" -m pytest -p no:logging packages/python -vv -k "$filter"
  coverage report -m
fi

mkdir -p m/.m
touch m/.m/pytest-ran
