#!/bin/bash
set -euo pipefail

coverage run --source packages/python/m -m unittest discover -s packages/python -v
coverage report -m --fail-under 72

# To run specific tests:
# python -m unittest discover -s packages/python -v -k test_instances
