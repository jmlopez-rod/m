#!/bin/bash

export PYTHONPATH="${PWD}/packages/python"

set -xeuo pipefail

# Only publish with the CI tool
[ "${M_CI:-False}" == "True" ] || exit 0

# this script should only be called by github.

# Release to pypi on releases
python3 -m twine upload .stage-pypi/dist/*

# Let github know we released
m github release --owner "$M_OWNER" --repo "$M_REPO" --version "$M_TAG"
