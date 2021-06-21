#!/bin/bash
set -euxo pipefail

# When releaseing we need to be in a clean state
[ "$(m git status)" == "clean" ] \
  || m message error 'releaseSetup.sh can only run in a clean git state'

gitBranch=$(m git branch)

# Only release from the master branch
[ "$gitBranch" == "master" ] \
  || m message error 'releases can be done only from the master branch'

# Gather info
git fetch --tags
currentVersion=$(git describe --tags || echo '0.0.0')
newVersion=$(m bump_version "$currentVersion")

# Swith to release branch
git checkout -b release \
  || m message error "Unable to switch to release branch"

# Update CHANGELOG and m.json files
m release_setup './m' "$newVersion"
