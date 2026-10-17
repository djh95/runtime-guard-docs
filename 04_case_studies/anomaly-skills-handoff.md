# Anomaly skills handoff (watcher)

**Rev:** `2026-10-17T2145+08` — **S84–S86 skills DONE (v3.6)**; S81–S83 v3.5; S78–S80 v3.4; S45 FAIL+GAP; S44 INVALID.  
Prior inbox `2026-10-17T2135+08` cleared by skills agent (162).

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
| PASS | S06, S08, S10′, S11, S12, S14, S16–S19, S20, S22–S26, S28–S43, S46–**S86** |
| FAIL / FAIL+GAP | S01, S07; **S45** |
| INVALID | **S44** |
| Parked | S02/S03/S05/S09 HARD; S04 HCCN; S13 BLOCKED; S15 skip; S21 HARD; S27 BLOCKED |
| **Builder** | check open set — skills on **162** |

## Inbox (160 → skills)

_empty — awaiting next 160 wave_

### Prior (skills done)

- **S86/S85/S84** | **skills done** v3.6 · L2 positions÷2 / temp÷50 / RMSNorm-out-negate
- **S83/S82/S81** | skills done v3.5 · L2 SwiGLU-input÷50 / cos_sin÷50 / attn-out×50
- **S80/S79/S78** | skills done v3.4
- **S77–S75** v3.3 · **S45** FAIL+GAP · **S44** INVALID

## Blocked note

- S21 HARD · S27 BLOCKED · S44 INVALID · S45 FAIL+GAP

## Skills verify

- S84/S85/S86: **DONE** v3.6 L2
- S81/S82/S83: DONE v3.5 · S78–S80: DONE v3.4 · S75–S77: DONE v3.3
- S45: FAIL+GAP · S44: INVALID
