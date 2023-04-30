#!/bin/bash

mVersion="${1:-latest}"

set -exuo pipefail

mPath=$(which m || echo '')
if [ "$mPath" == '' ]; then
  if [ "$mVersion" == 'latest' ]; then
    pip install jmlopez-m
  else
    pip install jmlopez-m==$mVersion
  fi
fi
