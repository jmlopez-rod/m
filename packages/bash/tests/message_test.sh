#!/bin/bash

testMessageNonCiEnv() {
  msg=$(m message open 'name' 'description')
  assertEquals "message open" "name: description" "$msg"

  msg=$(m message close 'name')
  assertEquals "message close" "" "$msg"

  msg=$(m message sibling_block 'block1' 'block2' 'block2-description')
  assertEquals "message close" 'block2: block2-description' "$msg"

  msg=$(m message warn 'warning message' 2>&1)
  assertEquals "message warn" "warn: warning message" "$msg"

  msg=$(m message warn --file app.js --line 1 --col 1 'warning message' 2>&1)
  assertEquals "message warn" "warn[app.js:1:1]: warning message" "$msg"

  msg=$(m message error 'error message' 2>&1)
  code=$?
  assertEquals "message error exit code" "1" "$code"
  assertEquals "message error" "error: error message" "$msg"

  msg=$(m message error --file app.js --line 1 --col 1 'error message' 2>&1)
  assertEquals "message error" "error[app.js:1:1]: error message" "$msg"
}

testMessageGithubActionsEnv() {
  export GITHUB_ACTIONS=true

  msg=$(m message open 'name' 'description')
  assertEquals "message open" "::group::name" "$msg"

  msg=$(m message close 'name')
  assertEquals "message close" "::endgroup::" "$msg"

  msg=$(m message sibling_block 'block1' 'block2' 'block2-description')
  assertEquals "message close" '::endgroup::
::group::block2' "$msg"

  msg=$(m message warn 'warning message' 2>&1)
  assertEquals "message warn" "::warning::warning message" "$msg"

  msg=$(m message warn --file app.js --line 1 --col 1 'warning message' 2>&1)
  assertEquals "message warn" "::warning file=app.js,line=1,col=1::warning message" "$msg"

  msg=$(m message error 'error message' 2>&1)
  code=$?
  assertEquals "message error exit code" "1" "$code"
  assertEquals "message error" "::error::error message" "$msg"

  msg=$(m message error --file app.js --line 1 --col 1 'error message' 2>&1)
  assertEquals "message error" "::error file=app.js,line=1,col=1::error message" "$msg"
  unset GITHUB_ACTIONS
}

testMessageTeamcityEnv() {
  export TC=true

  msg=$(m message open 'name' 'description')
  assertEquals "message open" "##teamcity[blockOpened name='name' description='description']" "$msg"

  msg=$(m message close 'name')
  assertEquals "message close" "##teamcity[blockClosed name='name']" "$msg"

  msg=$(m message sibling_block 'block1' 'block2' 'block2-description')
  assertEquals "message close" "##teamcity[blockClosed name='block1']
##teamcity[blockOpened name='block2' description='block2-description']" "$msg"

  msg=$(m message warn 'warning message' 2>&1)
  assertEquals "message warn" "##teamcity[message status='WARNING' text='warning message']" "$msg"

  msg=$(m message warn --file app.js --line 1 --col 1 'warning message' 2>&1)
  assertEquals "message warn" "##teamcity[message status='WARNING' text='|[app.js:1:1|]: warning message']" "$msg"

  msg=$(m message error 'error message' 2>&1)
  code=$?
  assertEquals "message error exit code" "1" "$code"
  assertEquals "message error" "##teamcity[buildProblem description='error message']" "$msg"

  msg=$(m message error --file app.js --line 1 --col 1 'error message' 2>&1)
  assertEquals "message error" "##teamcity[buildProblem description='|[app.js:1:1|]: error message']" "$msg"
}

. ./shunit2.sh
