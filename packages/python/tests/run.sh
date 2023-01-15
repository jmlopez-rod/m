#!/bin/bash
set -euo pipefail

coverage run --source packages/python/m -m pytest
coverage report -m --fail-under 74

# To run specific tests:
# python -m unittest discover -s packages/python -v -k tests.cli.commands.test_json.CliJsonTest
# python -m pytest -vv -k test_m_npm
