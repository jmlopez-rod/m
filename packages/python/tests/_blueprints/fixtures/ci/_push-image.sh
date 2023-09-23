#!/bin/bash
imageName=$1
set -euxo pipefail
docker tag staged-image:latest "ghcr.io/jmlopez-rod/$ARCH-$imageName:$M_TAG"
docker push "ghcr.io/jmlopez-rod/$ARCH-$imageName:$M_TAG"
