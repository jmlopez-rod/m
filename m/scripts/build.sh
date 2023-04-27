#!/bin/bash

export PYTHONPATH="${PWD}/packages/python"

set -xeuo pipefail

# source the m environment
m ci env m > /dev/null
source m/.m/env.list
export $(cut -d= -f1 m/.m/env.list)

m/scripts/build/pypi.sh || m message error 'pypi build failure'

# Only proceed with the CI tool
[ "$M_CI" == "True" ] || exit 0

{
  echo "m-is-release=$M_IS_RELEASE"
  echo "m-tag=$M_TAG"
} >> "$GITHUB_OUTPUT"
