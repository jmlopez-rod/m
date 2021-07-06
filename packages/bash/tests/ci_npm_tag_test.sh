#!/bin/bash

testNpmTag() {
  val=$(m ci npm_tag 0.0.0-develop.b123)
  assertEquals "branch name" "develop" "$val"

  val=$(m ci npm_tag 0.0.0-pr1234.b123)
  assertEquals "pr tag" "pr1234" "$val"

  val=$(m ci npm_tag 2.0.1-rc1234.b123)
  assertEquals "release candidate" "next" "$val"

  val=$(m ci npm_tag 2.0.1)
  assertEquals "sem version" "latest" "$val"
}

. ./shunit2.sh
