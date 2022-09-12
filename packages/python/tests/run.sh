#!/bin/bash
set -euo pipefail

# coverage run --source packages/python/m -m pytest
# coverage report -m --fail-under 80

# To run specific tests:
pytest packages/python -vv -k release_setup
