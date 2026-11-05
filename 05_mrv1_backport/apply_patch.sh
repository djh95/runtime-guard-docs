#!/usr/bin/env bash
# Apply MRV1 Runtime Guard wiring onto a clean BASE tree.
# Patches are generated against docs BASE (see <release>/BASE.md / CHANGELOG) —
# NOT against open PR tip trees. v0.26 / v0.30 tips may differ; do not checkout
# PR tip then apply these patches. See PR_COMMIT_MAP.md「如何读本表」.
#
# 2026-11-04 (RG06): enforces the documented BASE by default — target HEAD must
# match the per-release BASE SHA and the tree must be clean. Three-way merge is
# opt-in via --3way; --force-base skips the checks for verified-compatible trees.
# Usage:
#   apply_patch.sh --release v0.23.0 /path/to/vllm-ascend
#   apply_patch.sh /path/to/vllm-ascend            # auto-detect from describe/branch
#   apply_patch.sh --release v0.30.0 --3way /path  # opt into 3-way when strict fails
#   apply_patch.sh --release v0.30.0 --force-base /path  # expert: skip checks
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
RELEASE=""
TARGET=""
FORCE_BASE=0
THREE_WAY=0

SUPPORTED=(v0.23.0 v0.26.0rc1 v0.27.1rc1 v0.28.0rc1 v0.30.0)

usage() {
  echo "usage: $0 [--release <$(IFS='|'; echo "${SUPPORTED[*]}")>] [--force-base] [--3way] /path/to/vllm-ascend" >&2
  exit 2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --release) RELEASE="${2:-}"; shift 2 ;;
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

# Documented BASE commit per release — keep in sync with CHANGELOG.md
# (mrv1-rg.1「各 release BASE」table).
base_sha_for() {
  case "$1" in
    v0.23.0)    echo "5cb98caaadeff42b5b62b996e34bb2aaa29d20fd" ;;
    v0.26.0rc1) echo "f2f74a16c3c50a76f4349d807918e83edec1e35c" ;;
    v0.27.1rc1) echo "3b31886237ed65c435e0965b10e8002ff5769766" ;;
    v0.28.0rc1) echo "96df623103f921df1a4488170d106f36689acb59" ;;
    v0.30.0)    echo "6d25ba2b3c123bf963966cd583e985979d7a8a7d" ;;
    *)          echo "" ;;
  esac
}

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

HEAD_FULL="$(git -C "${TARGET}" rev-parse HEAD)"
EXPECTED_BASE="$(base_sha_for "${RELEASE}")"
if [[ "${FORCE_BASE}" -eq 1 ]]; then
  echo "WARNING: --force-base skips BASE and clean-tree checks (HEAD=${HEAD_FULL:0:10})." >&2
else
  if [[ -z "${EXPECTED_BASE}" ]]; then
    echo "Refusing: no pinned BASE SHA for ${RELEASE}. Sync base_sha_for() with CHANGELOG.md, or pass --force-base." >&2
    exit 1
  fi
  if [[ "${HEAD_FULL}" != "${EXPECTED_BASE}" ]]; then
    # Documented alias: v0.23.0 patch also verifies on tag v0.23.0.post1.
    tag="$(git -C "${TARGET}" describe --tags --exact-match 2>/dev/null || true)"
    if [[ "${RELEASE}" == "v0.23.0" && "${tag}" == "v0.23.0.post1" ]]; then
      echo "BASE check OK: HEAD is tagged v0.23.0.post1 (documented alias)."
    else
      echo "Refusing: HEAD ${HEAD_FULL:0:10} != documented BASE ${EXPECTED_BASE:0:10} for ${RELEASE} (see 05_mrv1_backport/CHANGELOG.md)." >&2
      echo "Checkout the documented BASE, or pass --force-base only if this tree is verified compatible." >&2
      exit 1
    fi
  fi
  if [[ -n "$(git -C "${TARGET}" status --porcelain 2>/dev/null)" ]]; then
    echo "Refusing: working tree is dirty (git status not empty)." >&2
    echo "Clean the tree, or pass --force-base only if you accept applying over local changes." >&2
    exit 1
  fi
  echo "BASE check OK: HEAD=${HEAD_FULL:0:10}, clean tree."
fi

echo "Applying ${#patches[@]} patch(es) from ${PATCH_DIR}"
if [[ -f "${HERE}/${RELEASE}/BASE.md" ]]; then
  echo "BASE note: ${HERE}/${RELEASE}/BASE.md"
fi

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

echo "OK: MRV1 Guard wiring applied for ${RELEASE}."
echo "Rebuild/install, then follow 01_enable_and_start/README.md (runtime-guard-docs; use Model Runner V1)."
echo "Record: git rev-parse HEAD && ls ${PATCH_DIR}"
