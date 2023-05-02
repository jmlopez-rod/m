#!/bin/bash

poetryVersion="${1:-latest}"

set -exuo pipefail

poetryPath=$(which poetry || echo '')
if [ "$poetryPath" == '' ]; then
  if [ "$poetryVersion" == 'latest' ]; then
    pip install poetry==$poetryVersion
  else
    pip install poetry==$poetryVersion
  fi
fi

{
  echo "POETRY_HOME=/opt/venv/poetry"
  echo "POETRY_CACHE_DIR=/opt/venv/.cache/pypoetry"
  echo "VIRTUAL_ENV=/opt/venv/workspace"
} >> "$GITHUB_ENV"

echo "/opt/venv/workspace/bin" >> $GITHUB_PATH
