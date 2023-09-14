#!/bin/bash

export PYTHONPATH="${PWD}/packages/python"

set -xeuo pipefail

# Only publish with the CI tool
[ "${GITHUB_ACTIONS:-False}" != "False" ] || exit 0

# this script should only be called by github.

# Release to pypi on releases
python3 -m twine upload .stage-pypi/dist/*

# Let github know we released
m github release --owner jmlopez-rod --repo m --version "$M_TAG"

# Create v tags
m git tag_release --version "$M_TAG" --major-only
