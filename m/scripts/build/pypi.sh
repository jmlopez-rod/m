#!/bin/bash
set -xeuo pipefail

target=.stage-pypi
binDir=./packages/bash/lib
buildDir=./m/scripts/build/pypi

rm -rf "$target"
mkdir -p "$target"
mkdir -p "$target/bin"

cp -r ./packages/python "./$target/src/"
cp "$binDir/m" "./$target/bin/m"
cp "$binDir/startRelease.sh" "./$target/bin/startRelease"
cp "$binDir/startHotfix.sh" "./$target/bin/startHotfix"
cp "$binDir/reviewRelease.sh" "./$target/bin/reviewRelease"
cp "$binDir/endRelease.sh" "./$target/bin/endRelease"
cp -r "$buildDir"/*  "./$target"
cp LICENSE README.md "./$target"

find "./$target" | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
rm -rf "./$target/src/tests"
sed -i -e "s/0.0.0-PLACEHOLDER/$M_PY_TAG/g" "./$target/setup.py"
sed -i -e "s/0.0.0-PLACEHOLDER/$M_PY_TAG/g" "./$target/src/m/version.py"

(
  cd "$target"
  python -m build
)
