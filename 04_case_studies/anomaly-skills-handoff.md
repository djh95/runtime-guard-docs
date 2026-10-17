# Anomaly skills handoff (watcher)

Skills agent (162) watches this file + store copy for **new PASS / FAIL+GAP** rows from the **160 builder**.

Skills live in `analysis/skill/` (**v1.5**). Offline analyze only — **do not steal 160 cards**.

```bash
export RG_TEST=/path/to/runtime-guard-test
PYTHONPATH="$RG_TEST" python -m analysis.scripts.summarize_reports --report-dir <report>
PYTHONPATH="$RG_TEST" python -m analysis.scripts.score_completion_samples --sample-dir <samples>
PYTHONPATH="$RG_TEST" python -m analysis.scripts.verify_request_kv --report <r.json> --kv-dir <rank_dir>
```

## Current baseline (do not rebuild on 160)

| Bucket | IDs |
|--------|-----|
| PASS | S06, S08, S10′, S11, S12, S14, S16, S17, S18, S19, S20, S22, **S23**, **S24** |
| FAIL+GAP | S01, S07 |
| Parked | S02/S03/S05/S09 HARD; S04 HCCN-blocked; S13 BLOCKED; S15 skip; S21 HARD (trig=0) |
| **Builder** | **ACTIVE** — [Mine older fix PRs](bc-478850c3-0de1-5968-8c50-a40ea9cffe0d) on **160** (skills = **162** only) |

## Inbox (160 → skills)

- **S24 PASS** `2/48/48` token_repeat | 160 cards `12,13` | run `24_quant_scale_zero-20261017T104714` | evidence `tests/build-anomaly-env/fail-evidence/S24/` | constructed post-load W8A8 scale zero; ≠ S07; always-on; skills detect-only
  - **skills done** 2026-10-17: full loop (score false-GAP fixed); skills **v1.5**; note `docs/anomaly-skills-runs/S24-20261017.md` (162 offline, no 160 cards)
- **S23 PASS** `2/17/48` token_repeat | 160 cards `10,11` | run `23_weight_layer_corrupt-20261017T104359` | evidence `tests/build-anomaly-env/fail-evidence/S23/` | constructed post-load weight zero; always-on; skills detect-only
  - **skills done** 2026-10-17: full loop L1 detect-only; skills **v1.5**; note `docs/anomaly-skills-runs/S23-20261017.md` (162 offline, no 160 cards)
- **S22 PASS** `130/45/48` spec_acceptance | evidence `fail-evidence/S22/` | **skills done** v1.4
- **S20 PASS** `130/48/48` token_repeat | evidence `fail-evidence/S20/` | **skills done** v1.3

## Requests → Build-on-160

Living capability: [anomaly-skills-capability-20261017.md](anomaly-skills-capability-20261017.md).

1. **S23-weight-corrupt** — **DONE PASS** `2/17/48` (skills v1.5 loop closed).
2. **S24-quant-scale-always** — **DONE PASS** `2/48/48` (skills v1.5 loop closed).

160 builder: older-PR miner active. Skills stays on **162**; on new Inbox PASS/FAIL+GAP → analyze→optimize→re-verify → mirror `runtime-guard-docs` same turn. Do not steal 160 cards.

## Skills verify (2026-10-17)

Batch re-verify of S06/S08/S10′/S11/S12/S14/S16–S19 + S01/S07: **no skill edit** (v1.5 adequate). See `docs/anomaly-skills-runs/batch-pass-wave-20261017.md`.
