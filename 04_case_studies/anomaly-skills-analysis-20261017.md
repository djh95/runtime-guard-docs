# Anomaly skills-driven analysis — 2026-10-17

Owner: skills agent on lab **192.168.13.162** (`rg-162-test`). Did **not** take over 160 anomaly builds.  
Repo: [`runtime-guard-test`](https://github.com/djh95/runtime-guard-test) `main` (**skills v1.4**).  
Guard pin: G2 `f2aefd068`. Protocol: three layers = trigger / precision / detect.

## 1. Skills inventory

| Location | Contents |
|----------|----------|
| `analysis/skill/` | 5 Cursor skills: `investigation`, `detector-sweep`, `config-recommender`, `analysis`, `ref-kv-dump` + `SKILLS_METADATA.md` |
| `analysis/scripts/` | Offline CLI: summarize / correlate / verify / inspect / score_completion_samples / ref-feed / compare / stitch |
| `tests/build-anomaly-env/` | SPEC/overlay/fail-evidence (not skills; evidence consumed by analysis) |
| `runtime-guard-docs` | Handbook 01–03 (human); skills are executable mirror in test repo |

No `.cursor/skills/` tree in this repo — skills live under `analysis/skill/*/SKILL.md`.

## 2. Per-scenario localization (skills applied)

Evidence: `tests/build-anomaly-env/fail-evidence/Sxx/` + live 162 runs under `~/runtime-guard/canonical/results/anomaly-origin-20261016/` (S06/S07).

| ID | Result | Root-cause class | Detector behavior | Skills path used |
|----|--------|------------------|-------------------|------------------|
| **S06** | PASS | MoE topk→expert0 (routing bias) | `token_repeat` fired; report+dump on 162; **verify PASS** (54 `.pt`, all finite) | summarize → verify `--kv-dir` → inspect; score samples (repeat) |
| **S08** | PASS | slot/index→0 garbage | `token_repeat` | fail-evidence runs; class → recommender `token_repeat` |
| **S10′** | PASS | FullAttn recycle without zero | `token_repeat` (65/20/79) | investigation 3-layer + analysis summarize on archived notes |
| **S11** | PASS | MLA RoPE pad-tail | `token_repeat` (138/39/60) | summarize `report_sample.json` |
| **S12** | PASS | packed KV zero stride | `token_repeat` (132/1/79) | summarize |
| **S14** | PASS | MLA `o_proj` empty pad | `token_repeat` (128/5/60) | summarize ×3; `prepare_ref_inputs` OK; verify FAIL locally (container `dump_dir` not on Mac) |
| **S16** | PASS | GateLinear logits demote | `token_repeat` (372/5/60) | summarize |
| **S17** | PASS | skip routed_scaling_factor | `token_repeat` (448/43/60) | summarize |
| **S18** | PASS | skip shared+routed combine | `token_repeat` (370/15/58) | summarize via `sample_report` alias |
| **S19** | PASS | topk renorm skip | `token_repeat` (448/42/60) | summarize via alias |
| **S20** | PASS | softcap/softmax numeric overflow (constructed) | `token_repeat` 130/48/48 — all `!!!!`/token0; `logits_finite` not required | summarize + score (`token0_collapse`); no 160 cards |
| **S22** | PASS | spec residual resample no-SALT (#18657) | `spec_acceptance` 130/45/48 (rates 0–0.27) + some `token_repeat` | summarize; samples look normal (distributional) |
| **S01** | FAIL+GAP | KV skip-zero → finite mixed garbage | `logits_finite` armed, **detect=0** | `score_completion_samples` on samples; GAP recorded |
| **S07** | FAIL+GAP | W8A8 deq scale collapse → **48/48 identical** mixed garbage | `logits_finite` miss; `token_repeat` weak | score on 162 samples: `identical_across_requests=True`, `garbage_mixed_script`×48, `detector_gap_hint` set |

### Skill gaps found (pre-fix)

1. No three-layer (trigger/precision/detect) language in investigation.  
2. Empty report dir treated as “stop” — missed S01/S07 precision.  
3. No offline scorer for completion samples / identical-across-requests.  
4. `summarize_reports` ignored fail-evidence aliases `sample_report.json` / `report_sample.json`.  
5. Recommender/sweep did not document finite-garbage GAP vs `token_repeat` MoE/KV classes.  
6. Container `dump_dir` vs host path — verify needs `--kv-dir` rank override (now documented).

## 3. Skills improvements pushed

- **v1.4**: S22 spec resample RNG → `spec_acceptance` primary (distributional); ≠ S05/S20.  
- **v1.3** (`30d1963`): S20 overflow → `token_repeat`; score ignores pure bang GAP false-positive.  
- **v1.2** `SKILLS_METADATA` + investigation class table + 3-layer + GAP path.  
- **analysis** skill: Step 1b `score_completion_samples`; alias reports; `--kv-dir` remap.  
- **config-recommender** / **detector-sweep**: MoE/KV/overflow → `token_repeat`; finite garbage = known GAP.  
- **New script** `analysis/scripts/score_completion_samples.py` (+ `token0_collapse`).  
- **summarize_reports**: accept `sample_report.json` / `report_sample.json`.  
- UT: `tests/test_score_completion_samples_standalone.py` (3 passed).

## 4. Watch — 160 builder handoff

Status: **12 PASS** (S20+S22) **+ 2 FAIL+GAP**. S20/S22 inbox consumed.  
Watcher: [anomaly-skills-handoff.md](./anomaly-skills-handoff.md). Run notes: `docs/anomaly-skills-runs/`.

## 5. Notes

- Prefer published overlays / fail-evidence; no overlay rebuild this turn.  
- S06 `fail-evidence/S06/BLOCKED.md` is stale vs 162 PASS run `T081459`.  
- MoE routing class: KV dumps can be all-finite — finite ≠ healthy routing; rely on `token_repeat` + optional ref.
