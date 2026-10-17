# Anomaly skills handoff (watcher)

**Rev:** `2026-10-17T1745+08` — **S48 + S49 + S50 skills DONE (v2.4)**; S45 FAIL+GAP; S46/S47 v2.3; S44 INVALID.  
Prior inbox `2026-10-17T1735+08` cleared by skills agent (162).

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
| PASS | S06, S08, S10′, S11, S12, S14, S16–S19, S20, S22–S26, S28–S43, S46–**S50** |
| FAIL / FAIL+GAP | S01, S07; **S45** |
| INVALID | **S44** |
| Parked | S02/S03/S05/S09 HARD; S04 HCCN; S13 BLOCKED; S15 skip; S21 HARD; S27 BLOCKED |
| **Builder** | check open set — skills on **162** |

## Inbox (160 → skills)

_empty — awaiting next 160 wave_

### Prior (skills done)

- **S50/S49/S48** | **skills done** v2.4 · L2 residual-negate / attn×50 / swiglu-swap
- **S47/S46** | skills done v2.3
- **S45** | FAIL+GAP documented
- **S44** | INVALID vacated
- **S43/S42** | v2.2 · **S41–S39** v2.1 · **S38–S36** v2.0

## Blocked note

- S21 HARD · S27 BLOCKED · S44 INVALID · S45 FAIL+GAP (no amplifier retune)

## Skills verify

- S48/S49/S50: **DONE** v2.4 L2
- S46/S47: DONE v2.3
- S45: FAIL+GAP
- S44: INVALID
