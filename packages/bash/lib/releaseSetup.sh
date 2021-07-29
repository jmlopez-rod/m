#!/bin/bash
set -euxo pipefail

# When releaseing we need to be in a clean state
[ "$(m git status)" == "clean" ] \
  || m message error 'releaseSetup.sh can only run in a clean git state'

gitBranch=$(m git branch)

# TODO: Create command to verify that we are allowed to create a release
#  this involves adding a field to the releaseFrom object in m.json
# Only release from the master branch
# [ "$gitBranch" == "master" ] \
#   || m message error 'releases can be done only from the master branch'

# Gather info
git fetch --tags
currentVersion=$(git describe --tags || echo '0.0.0')
newVersion=$(m ci bump_version "$currentVersion")

# TODO: The release object may not specify the `release` branch. It may be
#  something else.
# Swith to release branch
git checkout -b release \
  || m message error "Unable to switch to release branch"

# Update CHANGELOG and m.json files
m ci release_setup './m' "$newVersion"
