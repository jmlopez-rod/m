#!/bin/bash
set -xeuo pipefail

curl -fsSL https://github.com/tamasfe/taplo/releases/latest/download/taplo-full-linux-x86_64.gz \
  | gzip -d - | install -m 755 /dev/stdin /usr/local/bin/taplo
chmod +x /usr/local/bin/taplo
