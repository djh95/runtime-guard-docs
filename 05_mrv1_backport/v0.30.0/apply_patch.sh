#!/usr/bin/env bash
# Thin wrapper: apply this release's MRV1 patch.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REL="$(basename "$HERE")"
exec "$HERE/../apply_patch.sh" --release "$REL" "${1:?usage: $0 /path/to/vllm-ascend}"
