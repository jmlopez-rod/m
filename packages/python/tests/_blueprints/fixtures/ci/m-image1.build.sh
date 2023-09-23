#!/bin/bash
export DOCKER_BUILDKIT=1
set -euxo pipefail

docker build \
  --build-arg ARCH="$ARCH" \
  --build-arg M_TAG= \
  --build-arg BUILDKIT_INLINE_CACHE=1 \
  --cache-from staged-image:cache \
  --file packages/python/tests/_blueprints/m_dir/docker/Dockerfile.image1 \
  --progress plain \
  --secret id=GITHUB_TOKEN \
  --tag staged-image:latest \
  --tag ghcr.io/jmlopez-rod/m-image1: \
  --target first \
  .
