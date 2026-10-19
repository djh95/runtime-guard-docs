---
cursor:
  subagentId: "bc-fea3f65c-820d-58a1-a9ad-17d3943fe455"
---

# Typical-cases reorg done (2026-10-19)

## Actions
1. Ensured full runs under `runtime-guard-test/docs/anomaly-skills-runs/` (135 + README).
2. Removed bulk `anomaly-skills-runs/` from `runtime-guard-docs/04_case_studies/`.
3. Added **15** short templates in `04_case_studies/examples/` (`S10′` → `S10p_*.md`).
4. Rewrote `04_case_studies/README.md` index.
5. **Did not** delete test `fail-evidence/`.

## Final `04_case_studies/` tree
- `examples/` — 15 md templates
- Analysis/policy md (capability, eval, score, mining policy, audit, PRINCIPLES, handoff, status, …)
- **No** bulk runs directory

## Keep IDs
S01, S10′, S11, S07, S23, S45, S43, S22, S06, S26, S25, S50, S48, S47, S33

## Commits
- `runtime-guard-docs` main **`f175e5d`** — keep 15 examples; delete bulk runs
- `runtime-guard-test` main **`0643b45`** — runs README (canonical); fail-evidence untouched

## `04` remains
- `examples/` (15) + ~15 analysis/policy/status md + README  
- **No** `anomaly-skills-runs/`
