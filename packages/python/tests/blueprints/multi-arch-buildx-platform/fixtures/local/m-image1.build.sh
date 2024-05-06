#!/bin/bash
export DOCKER_BUILDKIT=1
set -euxo pipefail

docker build \
  --build-arg ARCH=local \
  --build-arg M_TAG= \
  --file packages/python/tests/blueprints/multi-arch/m/docker/Dockerfile.image1 \
  --progress plain \
  --secret id=GITHUB_TOKEN \
  --tag ghcr.io/repo-owner/m-image1: \
  --tag staged-image:latest \
  --target first \
  .
