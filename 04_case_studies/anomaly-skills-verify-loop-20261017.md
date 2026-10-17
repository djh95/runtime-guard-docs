# Anomaly skills verify loop — 2026-10-17

**Rule:** analyze → edit skills → **re-run same evidence path** → record before→after. Do not stop at the edit.

Evidence host: fail-evidence offline (Mac / 162 analysis); **no 160 cards**.

## Process (going forward)

1. Baseline: `summarize_reports` + `score_completion_samples` (+ `verify_request_kv` if dump) on `fail-evidence/Sxx/`.
2. Patch `analysis/skill/` and/or scripts for the concrete gap.
3. Re-run the **same** commands on the **same** artifacts.
4. Append delta here + update [anomaly-skills-capability-20261017.md](./anomaly-skills-capability-20261017.md).
5. `git push origin main` (test repo); mirror case-study copy in `runtime-guard-docs` `04_case_studies/` when the capability matrix changes.

## S20 — softcap/softmax overflow (`!!!!` / token0)

| | Before (pre-v1.3) | After (re-verify @ `aaa5565` skills+docs) |
|--|-------------------|-------------------------------------------|
| summarize | `token_repeat` ×2 | same ✓ |
| score labels | `repeat` only (no `token0_collapse`) | `repeat` + **`token0_collapse`** ✓ |
| `detector_gap_hint` | **would fire** (identical+precision → false GAP) | **`None`** ✓ |
| skills narrative | overflow not in class table | investigation/recommender: **L2 class-hint**; not detect-only ✓ |
| Expected improvement? | — | **Yes** — no false GAP; class-hint language + label |

Re-run cmds:

```bash
PYTHONPATH=. python -m analysis.scripts.summarize_reports --report-dir tests/build-anomaly-env/fail-evidence/S20
PYTHONPATH=. python -m analysis.scripts.score_completion_samples --sample-dir tests/build-anomaly-env/fail-evidence/S20
```

(Reports live as `report_*.json` in that dir; samples as `c_*.json`.)

## S22 — spec residual resample no-SALT

| | Before (pre-v1.4) | After (re-verify) |
|--|-------------------|-------------------|
| summarize | mixed reports present | `spec_acceptance`×3 + `token_repeat`×2 ✓ |
| score on samples | empty labels / no garbage | same — **expected** (distributional) ✓ |
| skills narrative | no S22 / RNG-SALT class; risk of treating empty samples as「无异常」 | investigation + sweep + analysis: **L2 class** via `spec_acceptance` rates; ≠ S05/S20 ✓ |
| Expected improvement? | — | **Yes** — guidance fixed; score correctly does **not** invent text GAP |

Re-run:

```bash
PYTHONPATH=. python -m analysis.scripts.summarize_reports --report-dir tests/build-anomaly-env/fail-evidence/S22/reports
PYTHONPATH=. python -m analysis.scripts.score_completion_samples --sample-dir tests/build-anomaly-env/fail-evidence/S22/samples
```

## S23 — weight layer corrupt always-on (detect-only)

| | Before (pre-v1.5 @ `1f6fc18` evidence) | After (re-verify skills+score v1.5) |
|--|----------------------------------------|--------------------------------------|
| layers | **2 / 17 / 48** `token_repeat` | same ✓ |
| summarize | `token_repeat` ×2 (archived reports) | same ✓ |
| score labels | `repeat`×1; gap=`None` | same ✓ |
| skills narrative | stub「SPEC中 / 预期 L1」 | investigation/sweep/recommender/analysis: **L1 detect-only**; 禁止定位 weight ✓ |
| Expected improvement? | — | **Yes** — class guidance locked to detect-only; score already correct |

Re-run:

```bash
PYTHONPATH=. python -m analysis.scripts.summarize_reports --report-dir tests/build-anomaly-env/fail-evidence/S23/reports
PYTHONPATH=. python -m analysis.scripts.score_completion_samples --sample-dir tests/build-anomaly-env/fail-evidence/S23/samples
```

## S24 — W8A8 weight_scale zero always-on (detect-only; ≠ S07)

| | Before (pre-v1.5 @ `1f6fc18` evidence) | After (re-verify skills+score v1.5) |
|--|----------------------------------------|--------------------------------------|
| layers | **2 / 48 / 48** `token_repeat` | same ✓ |
| summarize | `token_repeat` ×2 | same ✓ |
| score labels | `digits`+`repeat`+`garbage_mixed_script` | same labels |
| `detector_gap_hint` | **false GAP** (`finite_garbage_or_identical…`) | **`None`** ✓ |
| skills narrative | stub「预期 L1/GAP」易与 S07 混谈 | **L1 detect-only**; mixed-sample ≠ wholesale GAP; ≠ S07 ✓ |
| Expected improvement? | — | **Yes** — clear false GAP; detect-only language; ≠ S07 |

Re-run:

```bash
PYTHONPATH=. python -m analysis.scripts.summarize_reports --report-dir tests/build-anomaly-env/fail-evidence/S24/reports
PYTHONPATH=. python -m analysis.scripts.score_completion_samples --sample-dir tests/build-anomaly-env/fail-evidence/S24/samples
```

## Remaining gaps (not closed by this loop)

- S22: summarize does not yet print `acceptance_rate` column — optional next script tweak.
- S01/S07: still detector GAP; skills only offline score.
- Weight/quant: still **cannot** localize which tensor/scale (by design).
