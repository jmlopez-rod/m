#!/bin/bash
set -xeuo pipefail

# source the m environment
m ci env m | m json
source m/.m/env.list
export $(cut -d= -f1 m/.m/env.list)


rm -rf .stage

cp -r ./packages ./.stage
cp ./package.json ./.stage/package.json

find ./.stage | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
rm -rf ./.stage/python/tests
rm -rf ./.stage/bash/tests
sed -i -e "s/0.0.0-PLACEHOLDER/$M_TAG/g" ./.stage/package.json

cd .stage && npm pack && cd ..

# Only publish with the CI tool
[ "$M_CI" == "True" ] || exit 0

npmTag=$(m ci npm_tag "$M_TAG")
npm publish .stage/*.tgz --tag "$npmTag"

# Only on release
[ "$M_IS_RELEASE" == "True" ] || exit 0
m github release --owner "$M_OWNER" --repo "$M_REPO" --version "$M_TAG"
