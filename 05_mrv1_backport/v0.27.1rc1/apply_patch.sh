#!/usr/bin/env bash
# Thin wrapper: apply this release's MRV1 patch.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REL="$(basename "$HERE")"
if [[ $# -lt 1 ]]; then
  echo "usage: $0 [--force-base] [--3way] /path/to/vllm-ascend" >&2
  exit 2
fi
exec "$HERE/../apply_patch.sh" --release "$REL" "$@"
