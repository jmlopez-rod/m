#!/bin/bash

set -xeuo pipefail

export DOCKER_BUILDKIT=1

docker build -t m-devcontainer -f packages/docker/Dockerfile.devcontainer .
