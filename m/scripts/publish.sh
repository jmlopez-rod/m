#!/bin/bash

export PYTHONPATH="${PWD}/packages/python"
export PATH="${PWD}/packages/bash/lib:$PATH"

set -xeuo pipefail

# source the m environment
m ci env m > /dev/null
source m/.m/env.list
export $(cut -d= -f1 m/.m/env.list)

m/scripts/build/github.sh || m message error 'github build failure'
m/scripts/build/pypi.sh || m message error 'pypi build failure'

# Only publish with the CI tool
[ "$M_CI" == "True" ] || exit 0

# Only publishing to github on every pr and master branch
npmTag=$(m ci npm_tag "$M_TAG")
npm publish .stage-github/*.tgz --tag "$npmTag"

# Only on release
[ "$M_IS_RELEASE" == "True" ] || exit 0
m github release --owner "$M_OWNER" --repo "$M_REPO" --version "$M_TAG"

# Release to pypi and npmjs on releases
python3 -m twine upload .stage-pypi/dist/*
