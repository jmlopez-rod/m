#!/bin/bash

set -exuo pipefail

mPath=$(which m || echo '')
if [ "$mPath" == '' ]; then
  echo 'm is not installed'
else
  echo 'installed'
fi
