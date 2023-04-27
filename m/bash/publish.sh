#!/bin/bash

set -xeuo pipefail

pyVer=${PY_VER:-311}
img="ghcr.io/jmlopez-rod/m-devcontainer-py${pyVer}"

docker tag m-devcontainer "$img"
docker push "$img"
