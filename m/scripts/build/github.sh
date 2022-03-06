#!/bin/bash
set -xeuo pipefail

target=.stage-github
buildDir=./m/scripts/build/github

rm -rf "$target"

cp -r ./packages "./$target"
cp "$buildDir/package.json" "./$target/package.json"

find "./$target" | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
rm -rf "./$target/python/tests"
rm -rf "./$target/bash/tests"
sed -i -e "s/0.0.0-PLACEHOLDER/$M_TAG/g" "./$target/package.json"
sed -i -e "s/0.0.0-PLACEHOLDER/$M_TAG/g" "./$target/python/m/version.py"

(
  cd $target
  npm pack
)
