#!/usr/bin/env bash
# Apply Runtime Guard backport patches onto a v0.30.x vllm-ascend tree.
#
# 2026-11-04 (RG06): enforces the documented BASE by default — target HEAD must
# be 6d25ba2b3 (see CHANGELOG v0.30-rg.3) and the tree must be clean. Three-way
# merge is opt-in via --3way; --force-base skips the checks for expert trees.
# Usage: apply_patch.sh [--force-base] [--3way] /path/to/vllm-ascend
set -euo pipefail

TARGET=""
FORCE_BASE=0
THREE_WAY=0
HERE="$(cd "$(dirname "$0")" && pwd)"
PATCH_DIR="${HERE}/patches"
EXPECTED_BASE="6d25ba2b3c123bf963966cd583e985979d7a8a7d"

usage() {
  echo "usage: $0 [--force-base] [--3way] /path/to/vllm-ascend-checkout" >&2
  exit 2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --force-base) FORCE_BASE=1; shift ;;
    --3way) THREE_WAY=1; shift ;;
    -h|--help) usage ;;
    *)
      if [[ -z "${TARGET}" ]]; then TARGET="$1"; shift
      else usage
      fi
      ;;
  esac
done

if [[ -z "${TARGET}" || ( ! -d "${TARGET}/.git" && ! -f "${TARGET}/.git" ) ]]; then
  usage
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

HEAD_FULL="$(git -C "${TARGET}" rev-parse HEAD)"
if [[ "${FORCE_BASE}" -eq 1 ]]; then
  echo "WARNING: --force-base skips BASE and clean-tree checks (HEAD=${HEAD_FULL:0:10})." >&2
else
  if [[ "${HEAD_FULL}" != "${EXPECTED_BASE}" ]]; then
    echo "Refusing: HEAD ${HEAD_FULL:0:10} != documented BASE ${EXPECTED_BASE:0:10} (see 05_v030_backport/CHANGELOG.md)." >&2
    echo "Checkout 6d25ba2b3c123bf963966cd583e985979d7a8a7d, or pass --force-base only if this tree is verified compatible." >&2
    exit 1
  fi
  if [[ -n "$(git -C "${TARGET}" status --porcelain 2>/dev/null)" ]]; then
    echo "Refusing: working tree is dirty (git status not empty)." >&2
    echo "Clean the tree, or pass --force-base only if you accept applying over local changes." >&2
    exit 1
  fi
  echo "BASE check OK: HEAD=${HEAD_FULL:0:10}, clean tree."
fi

echo "Applying ${#patches[@]} patch(es) from ${PATCH_DIR}"
cd "${TARGET}"

for p in "${patches[@]}"; do
  echo "==> $(basename "$p")"
  if git apply --check "$p" 2>/dev/null; then
    git apply "$p"
  elif [[ "${THREE_WAY}" -eq 1 ]]; then
    echo "==> strict check failed; applying with --3way (explicit opt-in)" >&2
    git apply --3way "$p" || { echo "FAILED: $p (--3way)" >&2; exit 1; }
  else
    echo "FAILED: strict apply check for $p" >&2
    git apply --check "$p" || true
    echo "Fix the tree/BASE (see message above), or re-run with --3way to opt into a three-way merge." >&2
    exit 1
  fi
done

echo "OK: all patches applied. Rebuild/install, then follow:"
echo "  01_enable_and_start/README.md  (runtime-guard-docs repo)"
echo "Record: git rev-parse HEAD && ls ${PATCH_DIR}"
