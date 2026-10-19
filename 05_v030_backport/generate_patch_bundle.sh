#!/usr/bin/env bash
# Maintainer: export a Runtime Guard backport patch for releases/v0.30.0
# (rc line; no formal tag v0.30.0). BASE must match CHANGELOG.md.
#
# Preferred (matches the release cherry-pick PR):
#   VLLM_ASCEND_GIT=/path/to/vllm-ascend \
#     ./generate_patch_bundle.sh --from-pr 18450
#
# Equivalent explicit refs (PR tip = feature + perf on releases/v0.30.0):
#   ./generate_patch_bundle.sh \
#     --base 60c99586c^ \
#     --source origin/cherry-pick/pr-16849-to-releases-v0.30.0
#
# Avoid diffing main tip → v0.30 with a path whitelist: that pulls main-era
# context and is not what CI cherry-picked. Prefer the PR branch.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
BASE=""
SOURCE=""
PR=""
OUT_DIR="${HERE}/patches"
REPO="${VLLM_ASCEND_GIT:-}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base) BASE="$2"; shift 2 ;;
    --source) SOURCE="$2"; shift 2 ;;
    --from-pr) PR="$2"; shift 2 ;;
    --out-dir) OUT_DIR="$2"; shift 2 ;;
    --repo) REPO="$2"; shift 2 ;;
    -h|--help)
      sed -n '1,20p' "$0"
      exit 0
      ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "${REPO}" || ! -d "${REPO}/.git" ]]; then
  echo "Set VLLM_ASCEND_GIT or --repo to a vllm-ascend clone with full history." >&2
  exit 2
fi

cd "${REPO}"

if [[ -n "${PR}" ]]; then
  case "${PR}" in
    18450)
      # Head branch of https://github.com/vllm-project/vllm-ascend/pull/18450
      SOURCE="${SOURCE:-origin/cherry-pick/pr-16849-to-releases-v0.30.0}"
      if ! git rev-parse --verify "${SOURCE}^{commit}" >/dev/null 2>&1; then
        echo "Fetching PR head…" >&2
        git fetch origin cherry-pick/pr-16849-to-releases-v0.30.0:refs/remotes/origin/cherry-pick/pr-16849-to-releases-v0.30.0
        SOURCE="origin/cherry-pick/pr-16849-to-releases-v0.30.0"
      fi
      # First Guard commit on that PR is the feature cherry-pick; its parent is BASE.
      FEATURE="$(git log --reverse --format='%H' --grep='Add runtime_guard control plane' "${SOURCE}" -1)"
      if [[ -z "${FEATURE}" ]]; then
        # Fallback: second-from-tip when tip is perf-only on top of feature.
        FEATURE="$(git rev-parse "${SOURCE}^")"
      fi
      BASE="${BASE:-${FEATURE}^}"
      ;;
    *)
      echo "Unknown --from-pr ${PR}; pass --base/--source explicitly." >&2
      exit 2
      ;;
  esac
fi

if [[ -z "${BASE}" || -z "${SOURCE}" ]]; then
  echo "Need --from-pr 18450, or both --base and --source." >&2
  exit 2
fi

git rev-parse --verify "${BASE}^{commit}" >/dev/null
git rev-parse --verify "${SOURCE}^{commit}" >/dev/null

mkdir -p "${OUT_DIR}"
find "${OUT_DIR}" -maxdepth 1 -name '*.patch' -delete

STAMP="$(date -u +%Y%m%d)"
BASE_SHORT="$(git rev-parse --short "${BASE}^{commit}")"
SRC_SHORT="$(git rev-parse --short "${SOURCE}^{commit}")"
OUT_PATCH="${OUT_DIR}/0001-runtime-guard-from-pr18450-${BASE_SHORT}-to-${SRC_SHORT}-${STAMP}.patch"

echo "Diff ${BASE}..${SOURCE} (full PR range, no whitelist) -> ${OUT_PATCH}"
# Full range: PR is already conflict-resolved against releases/v0.30.0.
git diff "${BASE}^{commit}" "${SOURCE}^{commit}" > "${OUT_PATCH}"

if [[ ! -s "${OUT_PATCH}" ]]; then
  echo "Empty diff — check refs." >&2
  rm -f "${OUT_PATCH}"
  exit 1
fi

LINES="$(wc -l < "${OUT_PATCH}" | tr -d ' ')"
echo "Wrote ${OUT_PATCH} (${LINES} lines)"
echo "Commits in range:"
git log --oneline "${BASE}^{commit}..${SOURCE}^{commit}"
echo "Next:"
echo "  1) apply_patch.sh on a clean tree at BASE=$(git rev-parse --short "${BASE}^{commit}")"
echo "  2) update CHANGELOG.md (version, PR, BASE, SOURCE, features)"
echo "  3) distribute 05_v030_backport/ including patches/"
