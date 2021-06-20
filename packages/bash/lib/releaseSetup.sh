#!/bin/bash
set -euxo pipefail

[ "$(m git status)" == "clean" ] \
  || m message error 'releaseSetup.sh can only run in a clean git state'

gitBranch=$(m git branch)
