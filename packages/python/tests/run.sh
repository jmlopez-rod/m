#!/bin/bash
set -euo pipefail

export PYTHONPATH=./src:${PYTHONPATH:-}

runTest() {
  echo "[test] $1" && python -m unittest "tests.$1"
}

# Running manually so that we may select which test to turn off while debugging.
runTest core.fp.OneOfTest
runTest core.issue.IssueTest
runTest ci.config.free_flow.ConfigFreeFlowTest
runTest ci.config.git_flow.ConfigGitFlowTest
runTest ci.config.m_flow.ConfigMFlowTest
runTest ci.git_env.GitEnvTest
runTest ci.release_env.ReleaseEnvTest
runTest ci.lint.LintTest
runTest github.ci_dataclasses.CiDataclassesTest
runTest core.io.IoTest
