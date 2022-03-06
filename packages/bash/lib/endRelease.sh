#!/bin/bash

# Adding to path so that npx can work: https://superuser.com/a/39995
pathadd() {
  if [ -d "$1" ] && [[ ":$PATH:" != *":$1:"* ]]; then
    PATH="$1${PATH:+":$PATH"}"
  fi
}
pathadd "${PWD}/node_modules/@PACKAGE_SCOPE/m/bash/lib"

set -euxo pipefail

# Check that there is a release file first - in case of calling on accident
[[ -f  m/.m/release.list ]] || m message error 'release file not found'

source m/.m/release.list
export $(cut -d= -f1 m/.m/release.list)
# The following envvars will be available:
#   WORKFLOW, VERSION, OWNER, REPO, PR, PR_DEV

merged=$(m github pr --owner "$OWNER" --repo "$REPO" "$PR" | m jsonq merged)
if [[ "$merged" != 'true' ]]; then
  m github merge_pr --owner "$OWNER" --repo "$REPO" "$PR" | m json
fi


if [ "$WORKFLOW" == 'git_flow' ]; then
  latest=$(m github latest_release --owner "$OWNER" --repo "$REPO")
  while [ "$latest" != "$VERSION" ]
  do
    echo "$(date): checking for latest release in 10 seconds"
    sleep 10
    latest=$(m github latest_release --owner "$OWNER" --repo "$REPO")
  done

  merged=$(m github pr --owner "$OWNER" --repo "$REPO" "$PR_DEV" | m jsonq merged)
  if [[ "$merged" != 'true' ]]; then
    m github merge_pr --owner "$OWNER" --repo "$REPO" "$PR_DEV" | m json
  fi
fi

rm m/.m/release.list
