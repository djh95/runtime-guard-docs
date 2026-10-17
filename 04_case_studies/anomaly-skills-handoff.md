# Anomaly skills handoff (watcher)

**Rev:** `2026-10-17T1835+08` — **S57–S59 skills DONE (v2.7)**; S51–S56 v2.5+v2.6; S48–S50 v2.4; S45 FAIL+GAP; S44 INVALID.  
Prior inbox `2026-10-17T1825+08` cleared by skills agent (162).

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
| PASS | S06, S08, S10′, S11, S12, S14, S16–S19, S20, S22–S26, S28–S43, S46–**S59** |
| FAIL / FAIL+GAP | S01, S07; **S45** |
| INVALID | **S44** |
| Parked | S02/S03/S05/S09 HARD; S04 HCCN; S13 BLOCKED; S15 skip; S21 HARD; S27 BLOCKED |
| **Builder** | check open set — skills on **162** |

## Inbox (160 → skills)

_empty — awaiting next 160 wave_

### Prior (skills done)

- **S59/S58/S57** | **skills done** v2.7 · L2 positions×2 / value-negate / key×50
- **S56/S55/S54** | skills done v2.6
- **S53/S52/S51** | v2.5 · **S50–S48** v2.4 · **S47/S46** v2.3 · **S45** FAIL+GAP · **S44** INVALID

## Blocked note

- S21 HARD · S27 BLOCKED · S44 INVALID · S45 FAIL+GAP

## Skills verify

- S57/S58/S59: **DONE** v2.7 L2
- S54–S56: DONE v2.6 · S51–S53: DONE v2.5
- S48–S50: DONE v2.4
- S45: FAIL+GAP · S44: INVALID
