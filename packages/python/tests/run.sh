#!/bin/bash
set -euo pipefail

export DEBUG_HTTP_INCLUDE_BODY=1

SINGLE=true
SINGLE=false

if [ "$SINGLE" = 'false' ]; then
  coverage run --source packages/python/m -m pytest
  coverage report -m --fail-under 90
else
# To run specific tests:
# python -m unittest discover -s packages/python -v -k tests.cli.commands.test_json.CliJsonTest
# python -m pytest -vv -k test_m_npm
  pytest packages/python -vv -k test_jsonq
fi
