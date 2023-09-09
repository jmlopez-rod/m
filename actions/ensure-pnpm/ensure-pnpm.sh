#!/bin/bash

pnpmVersion="${1:-latest}"

set -exuo pipefail

pnpmPath=$(which pnpm || echo '')
if [ "$pnpmPath" == '' ]; then
  if [ "$pnpmVersion" == 'latest' ]; then
    npm install -g pnpm
  else
    npm install -g "pnpm@$pnpmVersion"
  fi
fi

echo "store-path=$(pnpm store path)" >> $GITHUB_OUTPUT
