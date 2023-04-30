#!/bin/bash

set -exuo pipefail

mPath=$(which m || echo '')
if [ "$mPath" == '' ]; then
  pip install jmlopez-m
else
  echo 'installed'
fi
