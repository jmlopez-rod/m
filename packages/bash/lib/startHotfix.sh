#!/bin/bash

# Adding to path so that npx can work: https://superuser.com/a/39995
pathadd() {
  if [ -d "$1" ] && [[ ":$PATH:" != *":$1:"* ]]; then
    PATH="$1${PATH:+":$PATH"}"
  fi
}
pathadd "${PWD}/node_modules/@PACKAGE_SCOPE/m/bash/lib"

set -euxo pipefail

# Making sure we are releasing from the proper branch
#  git_flow: master
#  m_flow: master
m ci assert_branch --type hotfix m

# Make sure we are in a clean state
[ "$(m git status)" == "clean" ] \
  || m message error 'hotfixSetup.sh can only run in a clean git state'


# Gather info
owner=$(m jsonq @m/m.json owner)
repo=$(m jsonq @m/m.json repo)
currentVersion=$(m github latest_release --owner "$owner" --repo "$repo")
newVersion=$(m ci bump_version --type hotfix "$currentVersion")

# Swith to release branch
git checkout -b "hotfix/$newVersion" \
  || m message error "Unable to switch to hotfix/$newVersion branch"

# Update CHANGELOG and m.json files
m ci release_setup './m' "$newVersion"
