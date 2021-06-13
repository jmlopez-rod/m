#!/bin/sh
set -euo pipefail

export PYTHONPATH=./src:${PYTHONPATH:-}

runTest() {
  echo "[test] $1" && python -m unittest "tests.$1"
}

# Running manually so that we may select which test to turn off while debugging.
runTest core.fp.OneOfTest
runTest core.issue.IssueTest
