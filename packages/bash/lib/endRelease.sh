#!/bin/bash

set -euo pipefail

which curl > /dev/null 2>&1 || m message error 'curl is not installed'

# Check that there is a release file first - in case of calling on accident
[[ -f  m/.m/release.list ]] || m message error 'release file not found'

source m/.m/release.list
export $(cut -d= -f1 m/.m/release.list)
# The following envvars will be available:
#   WORKFLOW, VERSION, OWNER, REPO, PR, PR_DEV

set -euxo pipefail

merged=$(m github pr --owner "$OWNER" --repo "$REPO" "$PR" | m jsonq merged)
if [[ "$merged" != 'true' ]]; then
  m github merge_pr --owner "$OWNER" --repo "$REPO" "$PR" | m json
fi


if [ "$WORKFLOW" == 'git_flow' ]; then
  latest=$(curl --silent "https://api.github.com/repos/$OWNER/$REPO/releases/latest" | m jsonq tag_name)
  while [ "$latest" != "$VERSION" ]
  do
    echo "$(date): checking for latest release in 10 seconds"
    sleep 10
    latest=$(curl --silent "https://api.github.com/repos/$OWNER/$REPO/releases/latest" | m jsonq tag_name)
  done

  merged=$(m github pr --owner "$OWNER" --repo "$REPO" "$PR_DEV" | m jsonq merged)
  if [[ "$merged" != 'true' ]]; then
    m github merge_pr --owner "$OWNER" --repo "$REPO" "$PR_DEV" | m json
  fi
fi

rm m/.m/release.list
