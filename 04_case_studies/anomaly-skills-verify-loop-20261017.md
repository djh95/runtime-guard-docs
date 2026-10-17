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

## S29 / S30 / S31 — cast / null-block KV / residual drop (older-PR wave-2)

Evidence @ `9b59072` fail-evidence; skills **v1.7**. Offline / 162 — **no 160**.

| ID | Before (pre-v1.7) | After (re-verify) |
|----|-------------------|-------------------|
| **S29** layers | 132/14/48 `token_repeat` | same ✓ |
| **S29** score | `repeat`+`phrase_repeat`+`digits`; gap=`None` | same ✓ |
| **S29** skills | no cast class (risk conflate S20/S26) | **L2** logits fp16 demote; ≠ S20/S26 ✓ |
| **S30** layers | 2/14/48 | same ✓ |
| **S30** score | `repeat`+`phrase_repeat`×16; gap=`None` | same ✓ |
| **S30** skills | no null-block class | **L2** (#39444); ≠ S01/S10/S23/S24 ✓ |
| **S31** layers | 470/48/48 | same ✓ |
| **S31** score | identical `FieldType` `phrase_repeat`×48; gap=`None` | same ✓ |
| **S31** skills | risk conflate S26 | **L2** residual drop ≠ S26 ✓ |
| Expected? | — | **Yes** — three L2 class-hints; score already adequate |

```bash
PYTHONPATH=. python -m analysis.scripts.summarize_reports --report-dir tests/build-anomaly-env/fail-evidence/S29/reports
PYTHONPATH=. python -m analysis.scripts.score_completion_samples --sample-dir tests/build-anomaly-env/fail-evidence/S29/samples
# likewise S30 S31
```

## S32 / S33 — FIA FULL-graph pad + incomplete softcap (v1.8)

| | Before (pre-v1.8) | After (re-verify) |
|--|-------------------|-------------------|
| **S32** layers | 132/47/48 `token_repeat` | same ✓ |
| **S32** score | precision_hits=**4**（漏 `wN_M` unique pad） | **`pad_echo`×45** + hits=**48**; gap=`None` ✓ |
| **S32** skills | risk conflate S14 / undercount precision | **L2** #7144; ≠ S14; unique-pad guidance ✓ |
| **S33** layers | 132/15/48 `token_repeat` | same ✓ |
| **S33** score | `repeat`+`phrase_repeat`; gap=`None` | same ✓ |
| **S33** skills | risk conflate S20 overflow | **L2** incomplete softcap ≠ S20 ✓ |
| Expected? | — | **Yes** — score pad_echo + two L2 class-hints |

```bash
PYTHONPATH=. python -m analysis.scripts.summarize_reports --report-dir tests/build-anomaly-env/fail-evidence/S32/reports
PYTHONPATH=. python -m analysis.scripts.score_completion_samples --sample-dir tests/build-anomaly-env/fail-evidence/S32/samples
# likewise S33
```

## S34 / S35 — attn scale drop + causal-off (v1.9)

| | Before (pre-v1.9) | After (re-verify) |
|--|-------------------|-------------------|
| **S34** layers | 18/26/48 `token_repeat` | same ✓ |
| **S34** score | unique digit/junk hits~25; gap=`None` | same ✓ |
| **S34** skills | no attn-scale class (risk ≠S20/S32/S33) | **L2** wrong attn temp ✓ |
| **S35** layers | 136/46/48 `token_repeat` | same ✓ |
| **S35** score | `phrase_repeat`×48; gap=`None` | same ✓ |
| **S35** skills | no causal-off class (risk conflate S34) | **L2** future leak ≠ S34 ✓ |
| Expected? | — | **Yes** — two L2 attn class-hints; score already adequate |

```bash
PYTHONPATH=. python -m analysis.scripts.summarize_reports --report-dir tests/build-anomaly-env/fail-evidence/S34/reports
PYTHONPATH=. python -m analysis.scripts.score_completion_samples --sample-dir tests/build-anomaly-env/fail-evidence/S34/samples
# likewise S35
```

## S36 / S37 / S38 — temp blowup + pos-zero + RMSNorm skip (v2.0)

| | Before (pre-v2.0) | After (re-verify) |
|--|-------------------|-------------------|
| **S36** layers | 132/10/19 `token_repeat` | same ✓ |
| **S36** score | precision_hits=**4**（漏 unique id-echo） | **`unique_garbage`×30 / `id_echo`×9 / hits=33**; gap=`None` ✓ |
| **S36** skills | no wrong-T class | **L2** temp-scale blowup ≠ S29/S20 ✓ |
| **S37** layers | 132/35/48 `token_repeat` | same ✓ |
| **S37** score | digit/phrase_repeat; gap=`None` | same (+dot-collapse) ✓ |
| **S37** skills | risk conflate S25/S28 | **L2** pos-collapse ≠ S25/S28/S11 ✓ |
| **S38** layers | 188/48/48 **`logits_finite`** | same ✓ |
| **S38** score | `token0_collapse`×48; gap=`None` | same ✓ |
| **S38** skills | risk conflate S20 softcap | **L2** via **`logits_finite`**; ≠ S26/S31/S20 ✓ |
| Expected? | — | **Yes** — S36 score bump + three L2 class-hints |

```bash
PYTHONPATH=. python -m analysis.scripts.summarize_reports --report-dir tests/build-anomaly-env/fail-evidence/S36/reports
PYTHONPATH=. python -m analysis.scripts.score_completion_samples --sample-dir tests/build-anomaly-env/fail-evidence/S36/samples
# likewise S37 S38
```

## S39 / S40 / S41 — SwiGLU skip + RoPE skip + attn-out ×1000 (v2.1)

| | Before (pre-v2.1) | After (re-verify) |
|--|-------------------|-------------------|
| **S39** layers | 58/48/48 **`logits_finite`** | same ✓ |
| **S39** score | `token0_collapse`×48; gap=`None` | same ✓ |
| **S39** skills | risk conflate S26/S31/S38 | **L2** SwiGLU skip-silu ✓ |
| **S40** layers | 58/45/48 `token_repeat` | same ✓ |
| **S40** score | `phrase_repeat`×47; gap=`None` | same ✓ |
| **S40** skills | risk conflate S25/S28/S37 | **L2** RoPE skip (unrotated) ✓ |
| **S41** layers | 58/48/48 **`logits_finite`** | same ✓ |
| **S41** score | `token0_collapse`×48; gap=`None` | same ✓ |
| **S41** skills | risk conflate S34 softmax-scale | **L2** post-FA attn-out ×1000 ≠ S34 ✓ |
| Expected? | — | **Yes** — three L2 class-hints; score already adequate |

```bash
PYTHONPATH=. python -m analysis.scripts.summarize_reports --report-dir tests/build-anomaly-env/fail-evidence/S39/reports
PYTHONPATH=. python -m analysis.scripts.score_completion_samples --sample-dir tests/build-anomaly-env/fail-evidence/S39/samples
# likewise S40 S41
```

## S42 / S43 / S44 — RoPE phase + embed×100 + logits.zero_ (v2.2)

| | Before (pre-v2.2) | After (re-verify) |
|--|-------------------|-------------------|
| **S42** layers | 16/16/48 `token_repeat` | same ✓ |
| **S42** score | repeat/id_echo; gap=`None` | same ✓ |
| **S42** skills | no wrong-phase class | **L2** `-cos_sin` ≠ S37/S40/S25/S28 ✓ |
| **S43** layers | 16/40/48 `token_repeat` | same ✓ |
| **S43** score | precision_hits=**0**（纯 `\n` 漏标） | **`newline_collapse`×40**; gap=`None` ✓ |
| **S43** skills | no embed-scale class | **L2** embed×100 ≠ S23/S41 ✓ |
| **S44** layers | 16/48/48 `token_repeat` `!!!!` | same (evidence kept) |
| **S44** judgment | landed as PASS | **BLOCKED / invalid-synthetic** — `logits.zero_()` invents symptom (PRINCIPLES §2); negate→zero retune ≠ origin ✓ |
| Expected? | — | **Yes** — S42/S43 L2 + S43 score bump; S44 honest reject |

```bash
PYTHONPATH=. python -m analysis.scripts.summarize_reports --report-dir tests/build-anomaly-env/fail-evidence/S42/reports
PYTHONPATH=. python -m analysis.scripts.score_completion_samples --sample-dir tests/build-anomaly-env/fail-evidence/S42/samples
# likewise S43; S44 archived as BLOCKED only
```

## S45 / S46 / S47 — top-k flip GAP + penalty flip + K/V swap (v2.3)

| | Before (pre-v2.3) | After (re-verify) |
|--|-------------------|-------------------|
| **S45** layers | 16 / unique / 0 | same ✓ |
| **S45** score | `garbage_mixed_script`×44; hits=47; gap | same; **WHY_UNDETECTED** + ≥3 samples ✓ |
| **S45** skills | risk call INVALID / amplifier-retune | **FAIL+GAP** honest（同 S01/S07）；≠ S46 ✓ |
| **S46** layers | 16/48/48 `token_repeat` | same ✓ |
| **S46** score | digit/`1.1.1…` phrase_repeat×47; gap=`None` | same ✓ |
| **S46** skills | no penalty-polarity class | **L2** sign flip；≠ S45/S44 ✓ |
| **S47** layers | 58/37/48 `token_repeat` | same ✓ |
| **S47** score | mixed_script+phrase_repeat×48; gap=`None` | same ✓ |
| **S47** skills | risk conflate S34/S35/S41 | **L2** K/V swap ≠ those ✓ |
| Expected? | — | **Yes** — S46/S47 L2; S45 honest FAIL+GAP |

```bash
PYTHONPATH=. python -m analysis.scripts.summarize_reports --report-dir tests/build-anomaly-env/fail-evidence/S46/reports
PYTHONPATH=. python -m analysis.scripts.score_completion_samples --sample-dir tests/build-anomaly-env/fail-evidence/S45/samples
# likewise S46 S47; S45 reports empty (detect=0)
```

## S48 / S49 / S50 — residual negate + attn×50 + SwiGLU half-swap (v2.4)

| | Before (pre-v2.4) | After (re-verify) |
|--|-------------------|-------------------|
| **S48** layers | 100/48/48 **`logits_finite`** | same ✓ |
| **S48** score | `token0_collapse`×48; gap=`None` | same ✓ |
| **S48** skills | risk conflate S31/S38 | **L2** residual negate ✓ |
| **S49** layers | 18/22/48 `token_repeat` | same ✓ |
| **S49** score | unique_garbage/repeat; gap=`None` | same ✓ |
| **S49** skills | risk conflate S34/S41 | **L2** attn×50 ≠ those ✓ |
| **S50** layers | 58/48/48 **`logits_finite`** | same ✓ |
| **S50** score | `token0_collapse`×48; gap=`None` | same ✓ |
| **S50** skills | risk conflate S39 skip-silu | **L2** half-swap ≠ S39 ✓ |
| Expected? | — | **Yes** — three L2 class-hints |

```bash
PYTHONPATH=. python -m analysis.scripts.summarize_reports --report-dir tests/build-anomaly-env/fail-evidence/S48/reports
PYTHONPATH=. python -m analysis.scripts.score_completion_samples --sample-dir tests/build-anomaly-env/fail-evidence/S48/samples
# likewise S49 S50
```


## S51 / S52 / S53 — value×50 + query-negate + logits÷50 (v2.5)

| | Before (pre-v2.5) | After (re-verify) |
|--|-------------------|-------------------|
| **S51** layers | 58/48/48 `token_repeat` | same ✓ (slim pack: layers+WHY only) |
| **S51** skills | risk conflate S41/S47/S49 | **L2** V×50 ✓ |
| **S52** layers | 58/26/48 `token_repeat` | same ✓ |
| **S52** skills | risk conflate S47/S51/S42 | **L2** Q-negate ✓ |
| **S53** layers | 16/16/48 `token_repeat` | same ✓ |
| **S53** skills | risk conflate S36/S44 | **L2** logits÷50 ≠ those ✓ |
| Expected? | — | **Yes** — three L2; note reports/samples not in fail-evidence |

```bash
# slim evidence: layers.json + WHY_PASS.md (no reports/samples mirrors)
python -c "import json;print(json.load(open('tests/build-anomaly-env/fail-evidence/S51/layers.json'))['detect_by'])"
```


## S54 / S55 / S56 — key-negate + residual×50 + SwiGLU-input-negate (v2.6)

| | Before (pre-v2.6) | After (re-verify) |
|--|-------------------|-------------------|
| **S54** layers | 58/26/48 `token_repeat` | same ✓ (slim) |
| **S54** skills | risk conflate S47/S51/S52 | **L2** K-negate ✓ |
| **S55** layers | 100/48/48 **`logits_finite`** | same ✓ |
| **S55** skills | risk conflate S31/S38/S48 | **L2** residual×50 ✓ |
| **S56** layers | 58/48/48 **`logits_finite`** | same ✓ |
| **S56** skills | risk conflate S39/S50 | **L2** input-negate ✓ |
| Expected? | — | **Yes** — three L2; S51–S53 already v2.5 |

## Remaining gaps (not closed by this loop)

- S22: summarize does not yet print `acceptance_rate` column — optional next script tweak.
- S01/S07/**S45**: still detector GAP; skills only offline score.
- Weight/quant: still **cannot** localize which tensor/scale (by design).
- Soft-inv RoPE/RMSNorm: **cannot** localize Triton store / exact mul line (by design).
- S08/S10′: PASS report trees not fully mirrored in fail-evidence (status/WHY only for S10′; S08 local = pre-PASS attempts).
