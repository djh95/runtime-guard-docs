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


## S57 / S58 / S59 — positions×2 + value-negate + key×50 (v2.7)

| | Before (pre-v2.7) | After (re-verify) |
|--|-------------------|-------------------|
| **S57** layers | 132/48/48 `token_repeat` | same ✓ (slim) |
| **S57** skills | risk conflate S37 | **L2** positions×2 ✓ |
| **S58** layers | 58/48/48 **`logits_finite`** | same ✓ |
| **S58** skills | risk conflate S51/S47/S52/S54 | **L2** V-negate ✓ |
| **S59** layers | 58/15/48 `token_repeat` | same ✓ |
| **S59** skills | risk conflate S49/S51/S54 | **L2** K×50 ✓ |
| Expected? | — | **Yes** — three L2; S51–S56 already done |


## S60 / S61 / S62 — query×50 + hidden×50 + pre-norm x×50 (v2.8)

| | Before (pre-v2.8) | After (re-verify) |
|--|-------------------|-------------------|
| **S60** layers | 58/23/48 `token_repeat` | same ✓ (slim) |
| **S60** skills | risk conflate S52/S49/S51/S59 | **L2** Q×50 ✓ |
| **S61** layers | 16/16/48 `token_repeat` | same ✓ |
| **S61** skills | risk conflate S53/S43 | **L2** hidden×50 ✓ |
| **S62** layers | 100/48/48 **`logits_finite`** | same ✓ |
| **S62** skills | risk conflate S26/S38/S48/S55 | **L2** pre-norm x×50 ✓ |
| Expected? | — | **Yes** — three L2 |


## S63 / S64 / S65 — attn-out-negate + residual÷50 + logits×50 (v2.9)

| | Before (pre-v2.9) | After (re-verify) |
|--|-------------------|-------------------|
| **S63** layers | 58/48/48 **`logits_finite`** | same ✓ (slim) |
| **S63** skills | risk conflate S41 | **L2** attn-out negate ✓ |
| **S64** layers | 100/48/48 `token_repeat` | same ✓ |
| **S64** skills | risk conflate S48/S55 | **L2** residual÷50 ✓ |
| **S65** layers | 16/16/48 `token_repeat` | same ✓ |
| **S65** skills | risk conflate S53/S36 | **L2** logits×50 ✓ |
| Expected? | — | **Yes** — three L2 |


## S66 / S67 / S68 — RMSNorm-weight-negate + SwiGLU-out-negate + attn-scale÷50 (v3.0)

| | Before (pre-v3.0) | After (re-verify) |
|--|-------------------|-------------------|
| **S66** layers | 100/48/48 **`logits_finite`** | same ✓ (slim) |
| **S66** skills | risk conflate S26/S38/S48/S55/S62 | **L2** norm-weight negate ✓ |
| **S67** layers | 58/48/48 **`logits_finite`** | same ✓ |
| **S67** skills | risk conflate S39/S50/S56 | **L2** SwiGLU-out negate ✓ |
| **S68** layers | 18/33/48 `token_repeat` | same ✓ |
| **S68** skills | risk conflate S34/S49 | **L2** attn-scale÷50 ✓ |
| Expected? | — | **Yes** — three L2 |


## S69 / S70 / S71 — embed-negate + variance-eps×1000 + RMSNorm-weight×50 (v3.1)

| | Before (pre-v3.1) | After (re-verify) |
|--|-------------------|-------------------|
| **S69** layers | 16/26/48 **`logits_finite`** | same ✓ (slim) |
| **S69** skills | risk conflate S43 | **L2** embed negate ✓ |
| **S70** layers | 100/17/48 `token_repeat` | same ✓ |
| **S70** skills | risk conflate S26/S38/S66 | **L2** variance-eps×1000 ✓ |
| **S71** layers | 102/48/48 **`logits_finite`** | same ✓ |
| **S71** skills | risk conflate S66 | **L2** RMSNorm-weight×50 ✓ |
| Expected? | — | **Yes** — three L2 |


## S72 / S73 / S74 — SwiGLU-out×50 + RMSNorm-x-negate + RMSNorm-weight÷50 (v3.2)

| | Before (pre-v3.2) | After (re-verify) |
|--|-------------------|-------------------|
| **S72** layers | 58/48/48 **`logits_finite`** | same ✓ (slim) |
| **S72** skills | risk conflate S39/S50/S56/S67 | **L2** SwiGLU-out×50 ✓ |
| **S73** layers | 100/48/48 **`logits_finite`** | same ✓ |
| **S73** skills | risk conflate S48/S62 | **L2** RMSNorm-x-negate ✓ |
| **S74** layers | 100/48/48 `token_repeat` | same ✓ |
| **S74** skills | risk conflate S66/S71 | **L2** RMSNorm-weight÷50 ✓ |
| Expected? | — | **Yes** — three L2 |


## S75 / S76 / S77 — hidden÷50 + SwiGLU-input×50 + variance-eps÷1000 (v3.3)

| | Before (pre-v3.3) | After (re-verify) |
|--|-------------------|-------------------|
| **S75** layers | 16/16/48 `token_repeat` | same ✓ (slim) |
| **S75** skills | risk conflate S61/S53/S65 | **L2** hidden÷50 ✓ |
| **S76** layers | 58/48/48 **`logits_finite`** | same ✓ |
| **S76** skills | risk conflate S39/S50/S56/S67/S72 | **L2** SwiGLU-input×50 ✓ |
| **S77** layers | 100/16/48 `token_repeat` | same ✓ |
| **S77** skills | risk conflate S70 | **L2** variance-eps÷1000 ✓ |
| Expected? | — | **Yes** — three L2 |


## S78 / S79 / S80 — RMSNorm-x÷50 + cos_sin×50 + embed÷50 (v3.4)

| | Before (pre-v3.4) | After (re-verify) |
|--|-------------------|-------------------|
| **S78** layers | 100/38/48 `token_repeat` | same ✓ (slim) |
| **S78** skills | risk conflate S62/S73 | **L2** RMSNorm-x÷50 ✓ |
| **S79** layers | 58/22/48 `token_repeat` | same ✓ |
| **S79** skills | risk conflate S37/S40/S42/S25/S28 | **L2** cos_sin×50 ✓ |
| **S80** layers | 16/17/33 `token_repeat` | same ✓ |
| **S80** skills | risk conflate S43/S69 | **L2** embed÷50 ✓ |
| Expected? | — | **Yes** — three L2 |


## S81 / S82 / S83 — SwiGLU-input÷50 + cos_sin÷50 + attn-out×50 (v3.5)

| | Before (pre-v3.5) | After (re-verify) |
|--|-------------------|-------------------|
| **S81** layers | 58/48/48 `token_repeat` | same ✓ (slim) |
| **S81** skills | risk conflate S39/S50/S56/S76 | **L2** SwiGLU-input÷50 ✓ |
| **S82** layers | 58/27/48 `token_repeat` | same ✓ |
| **S82** skills | risk conflate S37/S40/S42/S79 | **L2** cos_sin÷50 ✓ |
| **S83** layers | 58/48/48 `token_repeat` | same ✓ |
| **S83** skills | risk conflate S41/S63 | **L2** attn-out×50 ✓ |
| Expected? | — | **Yes** — three L2 |


## S84 / S85 / S86 — positions÷2 + temp÷50 + RMSNorm-out-negate (v3.6)

| | Before (pre-v3.6) | After (re-verify) |
|--|-------------------|-------------------|
| **S84** layers | 132/44/48 `token_repeat` | same ✓ (slim) |
| **S84** skills | risk conflate S37/S57 | **L2** positions÷2 ✓ |
| **S85** layers | 132/15/48 `token_repeat` (T=0.8) | same ✓ |
| **S85** skills | risk conflate S36 | **L2** temp÷50 ✓ |
| **S86** layers | 100/48/48 **`logits_finite`** | same ✓ |
| **S86** skills | risk conflate S73/S66 | **L2** RMSNorm-out-negate ✓ |
| Expected? | — | **Yes** — three L2 |


## S87 / S88 / S89 — RMSNorm-out×50 + residual-post-negate + RMSNorm-out÷50 (v3.7)

| | Before (pre-v3.7) | After (re-verify) |
|--|-------------------|-------------------|
| **S87** layers | 100/48/48 **`logits_finite`** | same ✓ (slim) |
| **S87** skills | risk conflate S62/S86 | **L2** RMSNorm-out×50 ✓ |
| **S88** layers | 100/48/48 **`logits_finite`** | same ✓ |
| **S88** skills | risk conflate S48/S86 | **L2** residual-post-negate ✓ |
| **S89** layers | 100/48/48 `token_repeat` | same ✓ |
| **S89** skills | risk conflate S87/S78 | **L2** RMSNorm-out÷50 ✓ |
| Expected? | — | **Yes** — three L2 |


## S90 / S91 / S92 — residual-post×50 + residual-post÷50 + temp-skip (v3.8)

| | Before (pre-v3.8) | After (re-verify) |
|--|-------------------|-------------------|
| **S90** layers | 102/48/48 **`logits_finite`** | same ✓ (slim) |
| **S90** skills | risk conflate S55/S64/S88 | **L2** residual-post×50 ✓ |
| **S91** layers | 100/48/48 `token_repeat` | same ✓ |
| **S91** skills | risk conflate S90/S64/S88 | **L2** residual-post÷50 ✓ |
| **S92** layers | 132/0/47 `token_repeat` (T=0.8) | same ✓ |
| **S92** skills | risk conflate S36/S85；misread precision=0 as GAP | **L2** temp-skip；precision=0 expected ✓ |
| Expected? | — | **Yes** — three L2 |

```bash
# slim evidence: layers.json + WHY_PASS.md
python -c "import json;d=json.load(open('tests/build-anomaly-env/fail-evidence/S92/layers.json'));print(d['precision'], d['detect_by'])"
```

## S93 / S94 / S95 — residual←normed-x + residual↔x swap + temp-double (v3.9)

| | Before (pre-v3.9) | After (re-verify) |
|--|-------------------|-------------------|
| **S93** layers | 100/48/48 `token_repeat` | same ✓ (slim) |
| **S93** skills | risk conflate S31/S94/S88–S91 | **L2** residual←normed-x ✓ |
| **S94** layers | 100/48/48 **`logits_finite`** | same ✓ |
| **S94** skills | risk conflate S31/S93/S88 | **L2** residual↔x swap ✓ |
| **S95** layers | 132/9/48 `token_repeat` (T=0.8) | same ✓ |
| **S95** skills | risk conflate S36/S85/S92 | **L2** temp-double ✓ |
| Expected? | — | **Yes** — three L2 |

```bash
python -c "import json;d=json.load(open('tests/build-anomaly-env/fail-evidence/S95/layers.json'));print(d['precision'], d['detect_by'])"
```

## S96 / S97 / S98 — RMSNorm-weight=ones + residual-leak-add + min_p-skip (v4.0)

| | Before (pre-v4.0) | After (re-verify) |
|--|-------------------|-------------------|
| **S96** layers | 100/0/33 `token_repeat` | same ✓ (slim) |
| **S96** skills | risk conflate S66/S71/S74；misread precision=0 as GAP | **L2** weight=ones；precision=0 expected ✓ |
| **S97** layers | 100/48/48 **`logits_finite`** | same ✓ |
| **S97** skills | risk conflate S31/S93/S94/S88–S91 | **L2** residual-leak-add ✓ |
| **S98** layers | 132/0/48 `token_repeat` (T=0.8) | same ✓ |
| **S98** skills | risk conflate S36/S85/S92/S95/S46；misread precision=0 as GAP | **L2** min_p-skip；precision=0 expected ✓ |
| Expected? | — | **Yes** — three L2 |

```bash
python -c "import json;d=json.load(open('tests/build-anomaly-env/fail-evidence/S96/layers.json'));print(d['precision'], d['detect_by'])"
```

## S99 / S100 / S101 — top_p-skip + RMSNorm-bias=weight + cos/sin-half-swap (v4.1)

| | Before (pre-v4.1) | After (re-verify) |
|--|-------------------|-------------------|
| **S99** layers | 132/0/45 `token_repeat` (T=0.8) | same ✓ (slim) |
| **S99** skills | risk conflate S45/S98/temp；misread precision=0 as GAP | **L2** top_p-skip；precision=0 expected ✓ |
| **S100** layers | 100/48/48 `token_repeat` | same ✓ |
| **S100** skills | risk conflate S66/S71/S74/S96 | **L2** bias=weight ✓ |
| **S101** layers | 58/48/48 `token_repeat` | same ✓ |
| **S101** skills | risk conflate S42/S79–S82/S40/S25/S28 | **L2** cos/sin-half-swap ✓ |
| Expected? | — | **Yes** — three L2 |

```bash
python -c "import json;d=json.load(open('tests/build-anomaly-env/fail-evidence/S99/layers.json'));print(d['precision'], d['detect_by'])"
```

## S102 / S103 / S104 — RMSNorm-out-abs + SwiGLU-gate-only + rope-skip-key (v4.2)

| | Before (pre-v4.2) | After (re-verify) |
|--|-------------------|-------------------|
| **S102** layers | 100/48/48 `token_repeat` | same ✓ (slim) |
| **S102** skills | risk conflate S86/S87–S89 | **L2** out-abs ✓ |
| **S103** layers | 58/0/48 `token_repeat` | same ✓ |
| **S103** skills | risk conflate S39/S50/S56–S81；misread precision=0 as GAP | **L2** gate-only；precision=0 expected ✓ |
| **S104** layers | 58/48/48 `token_repeat` | same ✓ |
| **S104** skills | risk conflate S40/S25/S28/S101 | **L2** rope-skip-key ✓ |
| Expected? | — | **Yes** — three L2 |

```bash
python -c "import json;d=json.load(open('tests/build-anomaly-env/fail-evidence/S103/layers.json'));print(d['precision'], d['detect_by'])"
```

## S105 / S106 / S107 — rope-skip-query + residual-post-abs + SwiGLU-up-only (v4.3)

| | Before (pre-v4.3) | After (re-verify) |
|--|-------------------|-------------------|
| **S105** layers | 58/48/48 `token_repeat` | same ✓ (slim) |
| **S105** skills | risk conflate S104/S40/S25/S28/S101 | **L2** rope-skip-query ✓ |
| **S106** layers | 100/22/48 `token_repeat` | same ✓ |
| **S106** skills | risk conflate S88/S90–S91/S102 | **L2** residual-post-abs ✓ |
| **S107** layers | 58/48/48 `token_repeat` | same ✓ |
| **S107** skills | risk conflate S103/S39/S50 | **L2** SwiGLU-up-only ✓ |
| Expected? | — | **Yes** — three L2 |

```bash
python -c "import json;d=json.load(open('tests/build-anomaly-env/fail-evidence/S106/layers.json'));print(d['precision'], d['detect_by'])"
```

## S108 / S109 / S110 — hidden-abs + value-abs + RMSNorm-weight-abs (v4.4)

| | Before (pre-v4.4) | After (re-verify) |
|--|-------------------|-------------------|
| **S108** layers | 16/48/48 `token_repeat` | same ✓ (slim) |
| **S108** skills | risk conflate S61/S75 | **L2** hidden-abs ✓ |
| **S109** layers | 58/0/24 `token_repeat` | same ✓ |
| **S109** skills | risk conflate S58/S51；misread precision=0 as GAP | **L2** value-abs；precision=0 expected ✓ |
| **S110** layers | 100/19/48 `token_repeat` | same ✓ |
| **S110** skills | risk conflate S66/S71/S74/S96/S100 | **L2** weight-abs ✓ |
| Expected? | — | **Yes** — three L2 |

```bash
python -c "import json;d=json.load(open('tests/build-anomaly-env/fail-evidence/S109/layers.json'));print(d['precision'], d['detect_by'])"
```

## S111 / S112 / S113 — key-abs + embed-abs + cos/sin-abs (v4.5)

| | Before (pre-v4.5) | After (re-verify) |
|--|-------------------|-------------------|
| **S111** layers | 58/30/48 `token_repeat` | same ✓ (slim) |
| **S111** skills | risk conflate S54/S59/S109 | **L2** key-abs ✓ |
| **S112** layers | 16/34/46 `token_repeat` | same ✓ |
| **S112** skills | risk conflate S69/S43/S80 | **L2** embed-abs ✓ |
| **S113** layers | 58/0/48 `token_repeat` | same ✓ |
| **S113** skills | risk conflate S42/S79–S82/S101/S40；misread precision=0 as GAP | **L2** cos/sin-abs；precision=0 expected ✓ |
| Expected? | — | **Yes** — three L2 |

```bash
python -c "import json;d=json.load(open('tests/build-anomaly-env/fail-evidence/S113/layers.json'));print(d['precision'], d['detect_by'])"
```

## S114 / S115 / S116 — query-abs + SwiGLU-out-abs + RMSNorm-x-abs (v4.6)

| | Before (pre-v4.6) | After (re-verify) |
|--|-------------------|-------------------|
| **S114** layers | 58/47/48 `token_repeat` | same ✓ (slim) |
| **S114** skills | risk conflate S52/S60/S109/S111 | **L2** query-abs ✓ |
| **S115** layers | 58/29/48 `token_repeat` | same ✓ |
| **S115** skills | risk conflate S67/S72/S103/S107 | **L2** SwiGLU-out-abs ✓ |
| **S116** layers | 100/48/48 `token_repeat` | same ✓ |
| **S116** skills | risk conflate S73/S62/S78/S102 | **L2** RMSNorm-x-abs ✓ |
| Expected? | — | **Yes** — three L2 |

```bash
python -c "import json;d=json.load(open('tests/build-anomaly-env/fail-evidence/S116/layers.json'));print(d['precision'], d['detect_by'])"
```

## S117 / S118 / S119 — query÷50 + key÷50 + residual-pre-abs (v4.7)

| | Before (pre-v4.7) | After (re-verify) |
|--|-------------------|-------------------|
| **S117** layers | 58/34/48 `token_repeat` | same ✓ (slim) |
| **S117** skills | risk conflate S60/S52/S114 | **L2** query÷50 ✓ |
| **S117** score | digits+repeat | same ✓ |
| **S118** layers | 58/33/48 `token_repeat` | same ✓ |
| **S118** skills | risk conflate S59/S54/S111 | **L2** key÷50 ✓ |
| **S118** score | digits+repeat | same ✓ |
| **S119** layers | 102/41/48 `token_repeat` | same ✓ |
| **S119** skills | risk conflate S48/S55/S64/S106 | **L2** residual-pre-abs ✓ |
| **S119** score | mixed_script+phrase_repeat | same ✓ |
| Expected? | — | **Yes** — three L2 |

```bash
python -c "import json;d=json.load(open('tests/build-anomaly-env/fail-evidence/S119/layers.json'));print(d['precision'], d['detect_by'])"
```


## S120 / S121 / S122 — RMSNorm-weight=zeros + SwiGLU-input-abs + logits-abs (v4.8)

| | Before (pre-v4.8) | After (re-verify) |
|--|-------------------|-------------------|
| **S120** layers | 100/48/48 `token_repeat` | same ✓ (slim) |
| **S120** skills | risk conflate S96/S66/S71/S74/S110 | **L2** weight=zeros ✓ |
| **S120** score | repeat+token0_collapse | same ✓ |
| **S121** layers | 58/0/48 `token_repeat` | same ✓ |
| **S121** skills | risk conflate S56/S76/S81/S115 or false GAP | **L2** input-abs；**precision=0 OK** ✓ |
| **S121** score | garbage_mixed_script+repeat | same ✓（detect>0 → not GAP） |
| **S122** layers | 16/16/48 `token_repeat` | same ✓ |
| **S122** skills | risk conflate S53/S65/S108 | **L2** logits-abs ✓ |
| **S122** score | digits/repeat (+unique) | same ✓ |
| Expected? | — | **Yes** — three L2 |

```bash
python -c "import json;d=json.load(open('tests/build-anomaly-env/fail-evidence/S121/layers.json'));print(d['precision'], d['detect_by'])"
```


## S123 / S124 / S125 — RMSNorm-bias=-weight + penalty-skip + residual-leak-sub (v4.9)

| | Before (pre-v4.9) | After (re-verify) |
|--|-------------------|-------------------|
| **S123** layers | 100/33/48 `token_repeat` | same ✓ (slim) |
| **S123** skills | risk conflate S100/S66/S120 | **L2** bias=-weight ✓ |
| **S123** score | mixed_script+repeat | same ✓ |
| **S124** layers | 132/0/48 `token_repeat` | same ✓ |
| **S124** skills | risk conflate S46/S98/S99 or false GAP | **L2** penalty-skip；**precision=0 OK** ✓ |
| **S124** score | id_echo+unique_garbage | same ✓（detect>0 → not GAP） |
| **S125** layers | 100/48/48 `logits_finite` | same ✓ |
| **S125** skills | risk conflate S97/S93/S94/S31 | **L2** residual-leak-sub via **logits_finite** ✓ |
| **S125** score | repeat+token0_collapse | same ✓ |
| Expected? | — | **Yes** — three L2 |

```bash
python -c "import json;d=json.load(open('tests/build-anomaly-env/fail-evidence/S124/layers.json'));print(d['precision'], d['detect_by'])"
```


## S126 / S127 / S128 — hidden-zeros + embed-zeros + cos/sin-zeros (v5.0)

| | Before (pre-v5.0) | After (re-verify) |
|--|-------------------|-------------------|
| **S126** layers | 16/48/48 `token_repeat` | same ✓ (slim) |
| **S126** skills | risk conflate S61/S75/S108/S122 | **L2** hidden-zeros ✓ |
| **S126** score | repeat+token0_collapse | same ✓ |
| **S127** layers | 16/48/48 `token_repeat` | same ✓ |
| **S127** skills | risk conflate S69/S43/S80/S112 | **L2** embed-zeros ✓ |
| **S127** score | repeat+token0_collapse | same ✓ |
| **S128** layers | 58/28/48 `token_repeat` | same ✓ |
| **S128** skills | risk conflate S42/S79–S82/S101/S113 | **L2** cos/sin-zeros ✓ |
| **S128** score | repeat+phrase_repeat | same ✓ |
| Expected? | — | **Yes** — three L2 |

```bash
python -c "import json;d=json.load(open('tests/build-anomaly-env/fail-evidence/S128/layers.json'));print(d['precision'], d['detect_by'])"
```


## S129 / S130 / S131 — residual-pre-zeros + query-zeros + SwiGLU-out-zeros (v5.1)

| | Before (pre-v5.1) | After (re-verify) |
|--|-------------------|-------------------|
| **S129** layers | 100/48/48 `token_repeat` | same ✓ (slim) |
| **S129** skills | risk conflate S48/S55/S64/S119 | **L2** residual-pre-zeros ✓ |
| **S129** score | phrase_repeat+repeat | same ✓ |
| **S130** layers | 58/28/48 `token_repeat` | same ✓ |
| **S130** skills | risk conflate S60/S52/S114/S117 | **L2** query-zeros ✓ |
| **S130** score | repeat+phrase_repeat | same ✓ |
| **S131** layers | 58/48/48 `token_repeat` | same ✓ |
| **S131** skills | risk conflate S67/S72/S115/S103/S107 | **L2** SwiGLU-out-zeros ✓ |
| **S131** score | repeat | same ✓ |
| Expected? | — | **Yes** — three L2 |

```bash
python -c "import json;d=json.load(open('tests/build-anomaly-env/fail-evidence/S131/layers.json'));print(d['precision'], d['detect_by'])"
```


## S132 / S133 / S134 — key-zeros + SwiGLU-input-zeros + cos/sin-ones (v5.2)

| | Before (pre-v5.2) | After (re-verify) |
|--|-------------------|-------------------|
| **S132** layers | 58/28/48 `token_repeat` | same ✓ (slim) |
| **S132** skills | risk conflate S54/S59/S111/S118 | **L2** key-zeros ✓ |
| **S132** score | repeat+phrase_repeat | same ✓ |
| **S133** layers | 58/48/48 `token_repeat` | same ✓ |
| **S133** skills | risk conflate S56/S76/S81/S121/S131 | **L2** SwiGLU-input-zeros ✓ |
| **S133** score | repeat | same ✓ |
| **S134** layers | 58/48/48 `token_repeat` | same ✓ |
| **S134** skills | risk conflate S42/S79–S82/S101/S113/S128 | **L2** cos/sin-ones ✓ |
| **S134** score | phrase_repeat+repeat | same ✓ |
| Expected? | — | **Yes** — three L2 |

```bash
python -c "import json;d=json.load(open('tests/build-anomaly-env/fail-evidence/S134/layers.json'));print(d['precision'], d['detect_by'])"
```


## S135 / S136 / S137 — residual-post-zeros + RMSNorm-out-zeros + embed-ones (v5.3)

| | Before (pre-v5.3) | After (re-verify) |
|--|-------------------|-------------------|
| **S135** layers | 102/48/48 `token_repeat` | same ✓ (slim) |
| **S135** skills | risk conflate S88/S90/S91/S106/S129 | **L2** residual-post-zeros ✓ |
| **S135** score | phrase_repeat+repeat | same ✓ |
| **S136** layers | 100/48/48 `token_repeat` | same ✓ |
| **S136** skills | risk conflate S86/S87/S89/S102 | **L2** RMSNorm-out-zeros ✓ |
| **S136** score | repeat+token0_collapse | same ✓ |
| **S137** layers | 16/48/48 `token_repeat` | same ✓ |
| **S137** skills | risk conflate S69/S43/S80/S112/S127 | **L2** embed-ones ✓ |
| **S137** score | repeat+phrase_repeat | same ✓ |
| Expected? | — | **Yes** — three L2 |

```bash
python -c "import json;d=json.load(open('tests/build-anomaly-env/fail-evidence/S137/layers.json'));print(d['precision'], d['detect_by'])"
```


## S138 / S139 / S140 — hidden-ones + positions-ones + residual-pre-ones (v5.4)

| | Before (pre-v5.4) | After (re-verify) |
|--|-------------------|-------------------|
| **S138** layers | 16/48/48 `token_repeat` | same ✓ (slim) |
| **S138** skills | risk conflate S61/S75/S108/S126 | **L2** hidden-ones ✓ |
| **S138** score | repeat+phrase_repeat (`pl`) | same ✓ |
| **S139** layers | 132/37/48 `token_repeat` | same ✓ |
| **S139** skills | risk conflate S37/S57/S84 | **L2** positions-ones ✓ |
| **S139** score | digits+repeat+phrase_repeat | same ✓ |
| **S140** layers | 102/48/48 `token_repeat` | same ✓ |
| **S140** skills | risk conflate S48/S55/S64/S119/S129 | **L2** residual-pre-ones ✓ |
| **S140** score | phrase_repeat+repeat (`[code`) | same ✓ |
| Expected? | — | **Yes** — three L2 |

```bash
python -c "import json;d=json.load(open('tests/build-anomaly-env/fail-evidence/S140/layers.json'));print(d['precision'], d['detect_by'])"
```


## S141 / S142 / S143 — query-ones + key-ones + SwiGLU-out-ones (v5.5)

| | Before (pre-v5.5) | After (re-verify) |
|--|-------------------|-------------------|
| **S141** layers | 58/36/48 `token_repeat` | same ✓ (slim) |
| **S141** skills | risk conflate S60/S52/S114/S117/S130 | **L2** query-ones ✓ |
| **S141** score | digits/repeat/phrase_repeat/newline | same ✓ |
| **S142** layers | 58/28/48 `token_repeat` | same ✓ |
| **S142** skills | risk conflate S54/S59/S111/S118/S132 | **L2** key-ones ✓ |
| **S142** score | repeat+phrase_repeat | same ✓ |
| **S143** layers | 58/48/48 `token_repeat` | same ✓ |
| **S143** skills | risk conflate S67/S72/S115/S131 | **L2** SwiGLU-out-ones ✓ |
| **S143** score | repeat+phrase_repeat (`造假`) | same ✓ |
| Expected? | — | **Yes** — three L2 |

```bash
python -c "import json;d=json.load(open('tests/build-anomaly-env/fail-evidence/S143/layers.json'));print(d['precision'], d['detect_by'])"
```


## S144 / S145 / S146 — residual-post-ones + RMSNorm-out-ones + SwiGLU-input-ones (v5.6)

| | Before (pre-v5.6) | After (re-verify) |
|--|-------------------|-------------------|
| **S144** layers | 100/48/48 `token_repeat` | same ✓ (slim) |
| **S144** skills | risk conflate S88/S90/S91/S106/S135 | **L2** residual-post-ones ✓ |
| **S144** score | phrase_repeat+repeat (`[code`) | same ✓ |
| **S145** layers | 100/48/48 `token_repeat` | same ✓ |
| **S145** skills | risk conflate S86/S87/S89/S102/S136 | **L2** RMSNorm-out-ones ✓ |
| **S145** score | repeat+phrase_repeat (`pl`) | same ✓ |
| **S146** layers | 58/48/48 `token_repeat` | same ✓ |
| **S146** skills | risk conflate S56/S76/S81/S121/S133 | **L2** SwiGLU-input-ones ✓ |
| **S146** score | repeat+phrase_repeat (`造假`) | same ✓ |
| Expected? | — | **Yes** — three L2 |

```bash
python -c "import json;d=json.load(open('tests/build-anomaly-env/fail-evidence/S146/layers.json'));print(d['precision'], d['detect_by'])"
```

## Remaining gaps (not closed by this loop)

- S22: summarize does not yet print `acceptance_rate` column — optional next script tweak.
- S01/S07/**S45**: still detector GAP; skills only offline score.
- Weight/quant: still **cannot** localize which tensor/scale (by design).
- Soft-inv RoPE/RMSNorm: **cannot** localize Triton store / exact mul line (by design).
- S08/S10′: PASS report trees not fully mirrored in fail-evidence (status/WHY only for S10′; S08 local = pre-PASS attempts).
