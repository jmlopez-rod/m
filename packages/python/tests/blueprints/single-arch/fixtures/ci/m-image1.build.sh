#!/bin/bash
export DOCKER_BUILDKIT=1
set -euxo pipefail

docker build \
  --build-arg ARCH=amd64 \
  --build-arg BUILDKIT_INLINE_CACHE=1 \
  --build-arg M_TAG= \
  --cache-from staged-image:cache \
  --file packages/python/tests/blueprints/single-arch/m/docker/Dockerfile.image1 \
  --progress plain \
  --secret id=GITHUB_TOKEN \
  --tag ghcr.io/repo-owner/m-image1: \
  --tag staged-image:latest \
  --target first \
  .
