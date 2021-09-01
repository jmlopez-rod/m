#!/bin/bash
set -euxo pipefail

# Making sure we are releasing from the proper branch
#  git_flow: develop
#  m_flow: master
m ci assert_branch --type release m

# Make sure we are in a clean state
[ "$(m git status)" == "clean" ] \
  || m message error 'releaseSetup.sh can only run in a clean git state'


# Gather info
git fetch --tags
currentVersion=$(git describe --tags || echo '0.0.0')
newVersion=$(m ci bump_version --type release "$currentVersion")

# Swith to release branch
git checkout -b "release/$newVersion" \
  || m message error "Unable to switch to release/$newVersion branch"

# Update CHANGELOG and m.json files
m ci release_setup './m' "$newVersion"
