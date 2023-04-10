#!/bin/bash

set -xeuo pipefail

img=${IMAGE:-devcontainer}
export DOCKER_BUILDKIT=1

docker build -t m-devcontainer -f "packages/docker/Dockerfile.$img" .
