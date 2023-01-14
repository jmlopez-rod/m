#!/bin/bash

set -xeuo pipefail

docker tag m-devcontainer ghcr.io/jmlopez-rod/m-devcontainer
docker push ghcr.io/jmlopez-rod/m-devcontainer
