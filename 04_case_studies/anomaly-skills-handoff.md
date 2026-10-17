# Anomaly skills handoff (watcher)

**Rev:** `2026-10-17T2230+08` — **S93–S95 skills DONE (v3.9)**; S90–S92 v3.8; S87–S89 v3.7; S45 FAIL+GAP; S44 INVALID.  
Prior inbox `2026-10-17T2125+08` cleared by skills agent (162).

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
| PASS | S06, S08, S10′, S11, S12, S14, S16–S19, S20, S22–S26, S28–S43, S46–**S95** |
| FAIL / FAIL+GAP | S01, S07; **S45** |
| INVALID | **S44** |
| Parked | S02/S03/S05/S09 HARD; S04 HCCN; S13 BLOCKED; S15 skip; S21 HARD; S27 BLOCKED |
| **Builder** | check open set — skills on **162** |

## Inbox (160 → skills)

_empty — awaiting next 160 wave_

### Prior (skills done)

- **S95/S94/S93** | **skills done** v3.9 · L2 residual←normed-x / residual↔x swap / temp-double
- **S92/S91/S90** | skills done v3.8 · L2 residual-post×50 / residual-post÷50 / temp-skip
- **S89/S88/S87** | skills done v3.7
- **S86–S84** v3.6 · **S45** FAIL+GAP · **S44** INVALID

## Blocked note

- S21 HARD · S27 BLOCKED · S44 INVALID · S45 FAIL+GAP

## Skills verify

- S93/S94/S95: **DONE** v3.9 L2
- S90/S91/S92: DONE v3.8 · S87–S89: DONE v3.7 · S84–S86: DONE v3.6
- S45: FAIL+GAP · S44: INVALID
