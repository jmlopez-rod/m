#!/bin/bash
set -xeuo pipefail

curl -LsSf https://astral.sh/uv/install.sh | sh

uv python install 3.11
