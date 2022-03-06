#!/bin/bash

export PYTHONPATH="${PWD}/packages/python"
export PATH="${PWD}/packages/bash/lib:$PATH"

set -xeuo pipefail

# source the m environment
m ci env m > /dev/null
source m/.m/env.list
export $(cut -d= -f1 m/.m/env.list)

m/scripts/build/npm.sh || m message error 'npm build failure'

# Only publish with the CI tool
[ "$M_CI" == "True" ] || exit 0

npmTag=$(m ci npm_tag "$M_TAG")
npm publish .stage-npm/*.tgz --tag "$npmTag"

# Only on release
[ "$M_IS_RELEASE" == "True" ] || exit 0
m github release --owner "$M_OWNER" --repo "$M_REPO" --version "$M_TAG"
