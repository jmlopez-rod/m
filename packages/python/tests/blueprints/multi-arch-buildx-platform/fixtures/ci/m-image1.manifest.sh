#!/bin/bash
set -euxo pipefail

docker buildx imagetools create \
  -t ghcr.io/repo-owner/m-image1:1.1.1 \
  -t ghcr.io/repo-owner/m-image1:latest \
  -t ghcr.io/repo-owner/m-image1:v1 \
  -t ghcr.io/repo-owner/m-image1:v1.1 \
  -t ghcr.io/repo-owner/m-image1:master \
  ghcr.io/repo-owner/m-image1:amd64-1.1.1 \
  ghcr.io/repo-owner/m-image1:arm64-1.1.1
