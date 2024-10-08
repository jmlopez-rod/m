#!/bin/bash
imageName=$1
set -euxo pipefail
docker tag staged-image:latest "ghcr.io/repo-owner/$imageName:$ARCH-$M_TAG"
docker push "ghcr.io/repo-owner/$imageName:$ARCH-$M_TAG"
