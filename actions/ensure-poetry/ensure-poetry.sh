#!/bin/bash

poetryVersion="${1:-latest}"
venvBasePath="${2:-/opt/venv}"
venvName="${3:-workspace}"

set -exuo pipefail

python3 -m venv "$venvBasePath/$venvName"
. "$venvBasePath/$venvName/bin/activate"

poetryPath=$(which poetry || echo '')
if [ "$poetryPath" == '' ]; then
  if [ "$poetryVersion" == 'latest' ]; then
    pip install poetry
  else
    pip install "poetry==$poetryVersion"
  fi
fi

{
  echo "POETRY_HOME=$venvBasePath/poetry"
  echo "POETRY_CACHE_DIR=$venvBasePath/.cache/pypoetry"
  echo "VIRTUAL_ENV=$venvBasePath/$venvName"
} >> "$GITHUB_ENV"

echo "$venvBasePath/$venvName/bin" >> $GITHUB_PATH
