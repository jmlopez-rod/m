#!/bin/bash
set -xeuo pipefail

docker run \
  --env PYTHONPATH="/checkout/packages/python" \
  --rm \
  -v "${PWD}":/checkout:z \
  -w /checkout \
  pyenv \
  "/checkout/m/scripts/checks/$1.sh"
