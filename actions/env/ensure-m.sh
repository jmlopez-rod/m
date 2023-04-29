#!/bin/bash

set -exuo pipefail

ls -al

mPath=$(which m)
if [ "$mPath" == '' ]; then
  echo 'm is not installed'
else
  echo 'installed'
fi
