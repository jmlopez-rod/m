#!/bin/bash
set -euo pipefail

coverage run -m unittest discover -s packages/python -v
coverage report -m --fail-under 80

# To run specific tests:
# python -m unittest discover -s packages/python -v -k test_instances
