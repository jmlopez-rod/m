#!/bin/bash
export DOCKER_BUILDKIT=1
set -euxo pipefail

docker buildx build --platform "$PLATFORM" --load \
  --build-arg ARCH="$ARCH" \
  --build-arg BUILDKIT_INLINE_CACHE=1 \
  --build-arg M_TAG= \
  --cache-from staged-image:cache \
  --file packages/python/tests/blueprints/multi-arch/m/docker/Dockerfile.image1 \
  --progress plain \
  --tag ghcr.io/repo-owner/m-image2: \
  --tag staged-image:latest \
  --target second \
  .
