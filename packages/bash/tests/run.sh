#!/bin/bash
set -euo pipefail

export PATH="../lib:$PATH"
export PYTHONPATH="../../python"

echo "bash version: $(bash --version)"
echo ""

# Add tests files in here. You may comment some files during development.
./message_test.sh
