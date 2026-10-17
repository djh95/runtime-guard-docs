# Anomaly skills handoff (watcher)

**Rev:** `2026-10-17T1312+08` — **Inbox CHANGE: S33 PENDING skills** (incomplete softcap).  
Prior rev `1305` marked S29–S31 PENDING; skills **v1.7** consumed them. Builder continues open set.

Skills agent (162) watches this file for **new PASS / FAIL+GAP**. Offline only — **do not steal 160 cards**.

```bash
export RG_TEST=/path/to/runtime-guard-test
PYTHONPATH="$RG_TEST" python -m analysis.scripts.summarize_reports --report-dir <report>
PYTHONPATH="$RG_TEST" python -m analysis.scripts.score_completion_samples --sample-dir <samples>
PYTHONPATH="$RG_TEST" python -m analysis.scripts.verify_request_kv --report <r.json> --kv-dir <rank_dir>
```

## Current baseline (do not rebuild on 160)

| Bucket | IDs |
|--------|-----|
| PASS | S06, S08, S10′, S11, S12, S14, S16–S19, S20, S22–S26, S28–**S31**, **S33** |
| FAIL+GAP | S01, S07 |
| Parked | S02/S03/S05/S09 HARD; S04 HCCN-blocked; S13 BLOCKED; S15 skip; S21 HARD (trig=0); **S27 BLOCKED** |
| **Builder** | **BUSY** — S32 (#7144) in flight; S21 retry next |

## Inbox (160 → skills) — PENDING

- **S33 PASS — PENDING skills** `132/15/48` token_repeat | 160 cards `8,9` | run `33_softcap_incomplete-20261017T130612` | evidence `tests/build-anomaly-env/fail-evidence/S33/` | incomplete softcap (÷cap+tanh skip *cap); ≠ S20 unstable

### Prior (skills done)

- **S31 PASS** `470/48/48` | **skills done** v1.7 residual-drop
- **S30 PASS** `2/14/48` | **skills done** v1.7 null-block KV
- **S29 PASS** `132/14/48` | **skills done** v1.7 logits fp16 demote
- **S28/S26/S25** | **skills done** v1.6
- **S24/S23/S22/S20** | **skills done** v1.5–v1.3

## Blocked note (not Inbox)

- **S27 BLOCKED** — pe-presliced MLA no-op. Skills skipped.

## Requests → Build-on-160

Builder: S32 FIA FULL-graph pad (#7144), then S21 dummy idle. Skills: process **S33 PENDING**.
