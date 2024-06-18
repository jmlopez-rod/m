#!/bin/bash
imageName=$1
set -euxo pipefail
docker tag staged-image:latest "ghcr.io/repo-owner/$imageName:1.1.1"
docker tag staged-image:latest "ghcr.io/repo-owner/$imageName:latest"
docker tag staged-image:latest "ghcr.io/repo-owner/$imageName:v1"
docker tag staged-image:latest "ghcr.io/repo-owner/$imageName:v1.1"
docker tag staged-image:latest "ghcr.io/repo-owner/$imageName:master"
docker image push --all-tags "ghcr.io/repo-owner/$imageName"
