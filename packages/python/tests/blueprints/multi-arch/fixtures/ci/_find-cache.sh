#!/bin/bash
imageName=$1
pullCache() {
  if docker pull -q "$1:$2" 2> /dev/null; then
    docker tag "$1:$2" "staged-image:cache"
  else
    return 1
  fi
}
findCache() {
  pullCache "$1" master || echo "NO CACHE FOUND"
}
set -euxo pipefail
findCache "ghcr.io/repo-owner/$imageName"
