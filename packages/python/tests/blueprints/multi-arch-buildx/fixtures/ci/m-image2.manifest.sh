#!/bin/bash
set -euxo pipefail

docker buildx imagetools create \
  -t ghcr.io/repo-owner/m-image2:1.1.1 \
  -t ghcr.io/repo-owner/m-image2:latest \
  -t ghcr.io/repo-owner/m-image2:v1 \
  -t ghcr.io/repo-owner/m-image2:v1.1 \
  -t ghcr.io/repo-owner/m-image2:master \
  ghcr.io/repo-owner/amd64-m-image2:1.1.1 \
  ghcr.io/repo-owner/arm64-m-image2:1.1.1
