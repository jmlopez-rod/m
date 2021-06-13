#!/bin/sh

# python 3.8.7
docker run \
  --rm \
  -v "$PWD":/checkout:z \
  -w /checkout \
  python:3.8.7-alpine \
  /checkout/src/tests/run.sh
