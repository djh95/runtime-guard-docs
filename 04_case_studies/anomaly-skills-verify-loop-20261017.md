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

## Batch wave — other PASS + FAIL+GAP (2026-10-17, offline / 162)

Scope: **S06, S08, S10′, S11, S12, S14, S16–S19** (+ re-check **S01/S07**). No 160 cards. Skills **v1.5** already covered these classes → **no skill edit** this wave; verify once and record.

| ID | Evidence used | summarize / score | Skills adequate? | Before→After |
|----|---------------|-------------------|------------------|--------------|
| **S06** | 162 pull → `fail-evidence/S06/` (replaced outdated BLOCKED) | `token_repeat`×1; labels `mixed_script`+`repeat`; gap=`None` | **Yes** L2 MoE | archive only; **no skill change** |
| **S08** | local dirs = early FAIL attempts only; PASS rates from status/docs | no PASS report archive locally | **Yes** L2 (+opt L3) slot class | **no change needed** (metadata) |
| **S10′** | `fail-evidence/S10/` status+WHY_PASS (65/20/79) | no report files archived | **Yes** L2–L3 potential KV | **no change needed** (metadata) |
| **S11** | `report_sample.json` | `token_repeat`×1 | **Yes** L2 MLA pad | **no change needed** |
| **S12** | `report_sample.json` | `token_repeat`×1 | **Yes** L2–L3 packed KV | **no change needed** |
| **S14** | reports×3 + samples×3 | `token_repeat`; labels digits/repeat/mixed; gap=`None` | **Yes** L2 | **no change needed** |
| **S16** | reports×3 + samples×3 | `token_repeat`; digits/repeat/token0; gap=`None` | **Yes** L2 MoE | **no change needed** |
| **S17** | report×1 + `c_000` | `token_repeat`; `repeat`; gap=`None` | **Yes** L2 MoE | **no change needed** |
| **S18** | `sample_report` + `c_000` | `token_repeat`; digits+repeat; gap=`None` | **Yes** L2 MoE | **no change needed** |
| **S19** | `sample_report` + `c_000` | `token_repeat`; `ctx_echo`; gap=`None` | **Yes** L2 MoE | **no change needed** |
| **S01** | status FAIL+GAP + `sample_01` | detect=0; single sample `mixed_script` (weak); no online detect | **Yes** GAP path | **no change** — still detector GAP |
| **S07** | 162 samples×48 + local exemplars | identical×48 `garbage_mixed_script`; **gap hint fires** | **Yes** GAP path | **no change** — still detector GAP |

### Batch verdict

- **PASS set:** detectors/`token_repeat` + skill class tables match evidence; **no false GAP** on scored PASS samples.
- **FAIL+GAP:** S01/S07 correctly remain offline-score / GAP; do not amplify.
- **Skills changed?** **No** (evidence hygiene only: S06 PASS archive).

## S25 / S26 / S28 — soft-inv RoPE / RMSNorm (older-PR mine)

Evidence @ `a2137bc` fail-evidence; skills **v1.6**. Host: offline / 162 — **no 160**.

| ID | Before (pre-v1.6) | After (re-verify) |
|----|-------------------|-------------------|
| **S25** layers | 462/15/48 `token_repeat` | same ✓ |
| **S25** score | `repeat`×9; gap=`None` | +`phrase_repeat`×9; gap=`None` ✓ |
| **S25** skills | no RoPE-half class (risk conflate S11) | investigation/recommender: **L2** RoPE half; ≠ S11 ✓ |
| **S26** layers | 470/14/48 | same ✓ |
| **S26** score | `repeat`×9; gap=`None` | +`phrase_repeat`; gap=`None` ✓ |
| **S26** skills | no RMSNorm dtype class | **L2** fp32-mul class ✓ |
| **S28** layers | 462/16/48 | same ✓ |
| **S28** score | **labels={}; precision_hits=0** (miss phrase loop) | **`phrase_repeat`×8 + `repeat`×8**; gap=`None` ✓ |
| **S28** skills | no style-flip class | **L2** neox→interleaved; ≠ S25/S11 ✓ |
| Expected? | — | **Yes** — S28 score blind spot closed; three L2 class-hints |

```bash
PYTHONPATH=. python -m analysis.scripts.summarize_reports --report-dir tests/build-anomaly-env/fail-evidence/S25/reports
PYTHONPATH=. python -m analysis.scripts.score_completion_samples --sample-dir tests/build-anomaly-env/fail-evidence/S25/samples
# likewise S26 S28
```

S27 BLOCKED — skipped (pe-presliced no-op + dirty clean).

## Remaining gaps (not closed by this loop)

- S22: summarize does not yet print `acceptance_rate` column — optional next script tweak.
- S01/S07: still detector GAP; skills only offline score.
- Weight/quant: still **cannot** localize which tensor/scale (by design).
- Soft-inv RoPE/RMSNorm: **cannot** localize Triton store / exact mul line (by design).
- S08/S10′: PASS report trees not fully mirrored in fail-evidence (status/WHY only for S10′; S08 local = pre-PASS attempts).
