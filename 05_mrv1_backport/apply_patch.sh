#!/usr/bin/env bash
# Apply MRV1 Runtime Guard wiring onto a clean BASE tree.
# Usage:
#   apply_patch.sh --release v0.23.0 /path/to/vllm-ascend
#   apply_patch.sh /path/to/vllm-ascend          # auto-detect from describe/branch
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
RELEASE=""
TARGET=""

SUPPORTED=(v0.23.0 v0.26.0rc1 v0.27.1rc1 v0.28.0rc1 v0.30.0)

usage() {
  echo "usage: $0 [--release <$(IFS='|'; echo "${SUPPORTED[*]}")>] /path/to/vllm-ascend" >&2
  exit 2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --release) RELEASE="${2:-}"; shift 2 ;;
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

detect_release() {
  local desc tag branch
  desc="$(git -C "${TARGET}" describe --tags --exact-match 2>/dev/null || true)"
  tag="${desc}"
  branch="$(git -C "${TARGET}" rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
  # normalize known aliases
  case "${tag}" in
    v0.23.0|v0.23.0.post1) echo v0.23.0; return ;;
    v0.26.0rc1) echo v0.26.0rc1; return ;;
    v0.27.1rc1) echo v0.27.1rc1; return ;;
    v0.28.0.rc1|v0.28.0rc1) echo v0.28.0rc1; return ;;
    v0.30.0rc1|v0.30.0rc2) echo v0.30.0; return ;;
  esac
  case "${branch}" in
    releases/v0.30.0|releases/v0.30.0rc*) echo v0.30.0; return ;;
  esac
  # BASE SHA match for v0.30 Guard-pre tip
  local full
  full="$(git -C "${TARGET}" rev-parse HEAD)"
  if [[ "${full}" == 6d25ba2b3c123bf963966cd583e985979d7a8a7d ]]; then
    echo v0.30.0; return
  fi
  return 1
}

if [[ -z "${RELEASE}" ]]; then
  if ! RELEASE="$(detect_release)"; then
    echo "Cannot auto-detect release; pass --release (${SUPPORTED[*]})." >&2
    exit 2
  fi
  echo "Auto-detected --release ${RELEASE}"
fi

ok=0
for s in "${SUPPORTED[@]}"; do
  [[ "${RELEASE}" == "${s}" ]] && ok=1 && break
done
if [[ "${ok}" -ne 1 ]]; then
  echo "Unsupported --release ${RELEASE}. Supported: ${SUPPORTED[*]}" >&2
  exit 2
fi

PATCH_DIR="${HERE}/${RELEASE}/patches"
if [[ ! -d "${PATCH_DIR}" ]]; then
  echo "missing patch dir: ${PATCH_DIR}" >&2
  exit 1
fi

shopt -s nullglob
patches=("${PATCH_DIR}"/*.patch)
if [[ ${#patches[@]} -eq 0 ]]; then
  echo "No *.patch under ${PATCH_DIR}." >&2
  exit 1
fi

echo "Target: ${TARGET}"
echo "Release: ${RELEASE}"
echo "Applying ${#patches[@]} patch(es) from ${PATCH_DIR}"
if [[ -f "${HERE}/${RELEASE}/BASE.md" ]]; then
  echo "BASE note: ${HERE}/${RELEASE}/BASE.md"
fi

cd "${TARGET}"
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

echo "OK: MRV1 Guard wiring applied for ${RELEASE}."
echo "Rebuild/install, then follow 01_enable_and_start/README.md (runtime-guard-docs; use Model Runner V1)."
echo "Record: git rev-parse HEAD && ls ${PATCH_DIR}"
