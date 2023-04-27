#!/bin/bash
set -xeuo pipefail

export DEBIAN_FRONTEND=noninteractive

apt clean
apt autoclean
apt-get update

apt-get install -y --fix-missing \
  git make \
  curl bash-completion
