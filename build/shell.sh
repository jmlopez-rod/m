#!/bin/bash
set -xeuo pipefail

docker run \
  -it \
  --env PYTHONPATH="/checkout/packages/python" \
  --rm \
  -v "${PWD}":/checkout:z \
  -w /checkout \
  pyenv \
  "/bin/bash"
