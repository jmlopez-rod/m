#!/bin/bash
set -xeuo pipefail

target=.stage-github
buildDir=./m/scripts/build/github

rm -rf "$target"
mkdir -p "$target"

cp -r ./packages/bash "./$target/bash"
cp -r ./packages/python "./$target/python"
cp "$buildDir/package.json" "./$target/package.json"
cp LICENSE README.md "./$target"

find "./$target" | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
rm -rf "./$target/python/tests"
rm -rf "./$target/bash/tests"
sed -i -e "s/0.0.0-PLACEHOLDER/$M_TAG/g" "./$target/package.json"
sed -i -e "s/0.0.0-PLACEHOLDER/$M_TAG/g" "./$target/python/m/version.py"

# Replacing scope in executables
SCOPE=jmlopez-rod
binDir="./$target/bash/lib"
sed -i -e "s/PACKAGE_SCOPE/$SCOPE/g" "$binDir/m"
sed -i -e "s/PACKAGE_SCOPE/$SCOPE/g" "$binDir/startHotfix.sh"
sed -i -e "s/PACKAGE_SCOPE/$SCOPE/g" "$binDir/startRelease.sh"
sed -i -e "s/PACKAGE_SCOPE/$SCOPE/g" "$binDir/reviewRelease.sh"
sed -i -e "s/PACKAGE_SCOPE/$SCOPE/g" "$binDir/endRelease.sh"

(
  cd $target
  npm pack
)
