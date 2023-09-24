#!/bin/bash
export DOCKER_BUILDKIT=1
set -euxo pipefail

docker build \
  --build-arg M_TAG= \
  --file packages/python/tests/blueprints/single-arch/m/docker/Dockerfile.image1 \
  --progress plain \
  --tag ghcr.io/repo-owner/m-image2: \
  --tag staged-image:latest \
  --target second \
  .
