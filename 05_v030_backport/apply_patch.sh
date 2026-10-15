#!/usr/bin/env bash
# Apply Runtime Guard backport patches onto a v0.30.x vllm-ascend tree.
# Usage: apply_patch.sh /path/to/vllm-ascend
set -euo pipefail

TARGET="${1:-}"
HERE="$(cd "$(dirname "$0")" && pwd)"
PATCH_DIR="${HERE}/patches"

if [[ -z "${TARGET}" || ( ! -d "${TARGET}/.git" && ! -f "${TARGET}/.git" ) ]]; then
  echo "usage: $0 /path/to/vllm-ascend-checkout" >&2
  exit 2
fi

if [[ ! -d "${PATCH_DIR}" ]]; then
  echo "missing patch dir: ${PATCH_DIR}" >&2
  exit 1
fi

shopt -s nullglob
patches=("${PATCH_DIR}"/*.patch)
if [[ ${#patches[@]} -eq 0 ]]; then
  echo "No *.patch under ${PATCH_DIR}." >&2
  echo "Ask the maintainer for the current v0.30-rg package, or run generate_patch_bundle.sh." >&2
  exit 1
fi

echo "Target: ${TARGET}"
echo "Applying ${#patches[@]} patch(es) from ${PATCH_DIR}"
cd "${TARGET}"

# Prefer git apply for 3-way when possible
for p in "${patches[@]}"; do
  echo "==> $(basename "$p")"
  if git apply --check "$p" 2>/dev/null; then
    git apply "$p"
  elif git apply --3way "$p"; then
    :
  else
    echo "FAILED: $p" >&2
    echo "Resolve conflicts, see git status, then report to maintainer." >&2
    exit 1
  fi
done

echo "OK: all patches applied. Rebuild/install, then follow:"
echo "  docs/wiki/runtime_guard/01_enable_and_start.md"
echo "Record: git rev-parse HEAD && ls ${PATCH_DIR}"
