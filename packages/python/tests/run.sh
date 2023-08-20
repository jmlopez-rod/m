#!/bin/bash
set -euo pipefail

export DEBUG_HTTP_INCLUDE_BODY=1

SINGLE=true
SINGLE=false

if [ "$SINGLE" = 'false' ]; then
  coverage run --source packages/python/m -m pytest -p no:logging
  coverage report -m --fail-under 100
else
# To run specific tests:
# python -m unittest discover -s packages/python -v -k tests.cli.commands.test_json.CliJsonTest
# python -m pytest -vv -k test_m_npm
  pytest -p no:logging packages/python -vv -k test_m_flow[tcase2]
fi

mkdir -p m/.m
touch m/.m/pytest-ran
