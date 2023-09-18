#!/bin/bash
set -xeuo pipefail

export DEBIAN_FRONTEND=noninteractive

apt-get install unzip -y
# https://github.com/denoland/deno
# install deno to give access to `lint` and `fmt`
curl -fsSL https://deno.land/install.sh | DENO_INSTALL=/usr/local sh

# remove unzip
apt -y purge unzip

