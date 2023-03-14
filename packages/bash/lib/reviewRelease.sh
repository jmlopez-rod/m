#!/bin/bash

# @deprecated - remove when moving to m 1.0.0

# Adding to path so that npx can work: https://superuser.com/a/39995
pathadd() {
  if [ -d "$1" ] && [[ ":$PATH:" != *":$1:"* ]]; then
    PATH="$1${PATH:+":$PATH"}"
  fi
}
pathadd "${PWD}/node_modules/@PACKAGE_SCOPE/m/bash/lib"

m message warn 'reviewRelease is deprecated - use `m review_release`'
m review_release
