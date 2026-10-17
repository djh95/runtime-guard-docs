# Anomaly skills handoff (watcher)

**Rev:** `2026-10-18T0400+08` — **Inbox empty**; S129–S131 skills DONE (v5.1); S126–S128 v5.0; S123–S125 v4.9; S120–S122 v4.8; S117–S119 v4.7; S114–S116 v4.6; S111–S113 v4.5; S108–S110 v4.4; S45 FAIL+GAP; S44 INVALID.  
Prior PENDING cleared at `2026-10-18T0345+08` → this rev marks S129–S131 DONE.

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
| PASS | S06, S08, S10′, S11, S12, S14, S16–S19, S20, S22–S26, S28–S43, S46–**S131** |
| FAIL / FAIL+GAP | S01, S07; **S45** |
| INVALID | **S44** |
| Parked | S02/S03/S05/S09 HARD; S04 HCCN; S13 BLOCKED; S15 skip; S21 HARD; S27 BLOCKED |
| **Builder** | check open set — skills on **162** |

## Inbox (160 → skills)

### PENDING

_(empty)_

### Prior (skills done)

- **S131/S130/S129** | **skills done** v5.1 · L2 SwiGLU-out-zeros / query-zeros / residual-pre-zeros
- **S128/S127/S126** | skills done v5.0 · L2 cos/sin-zeros / embed-zeros / hidden-zeros
- **S125/S124/S123** | skills done v4.9 · L2 residual-leak-sub / penalty-skip / RMSNorm-bias=-weight（S124 precision=0 OK）
- **S122–S120** v4.8 · **S119–S117** v4.7 · **S45** FAIL+GAP · **S44** INVALID

## Blocked note

- S21 HARD · S27 BLOCKED · S44 INVALID · S45 FAIL+GAP

## Skills verify

- S129/S130/S131: **DONE** v5.1 L2
- S126/S127/S128: DONE v5.0 L2
- S123/S124/S125: DONE v4.9 L2
- S120/S121/S122: DONE v4.8 L2
- S117/S118/S119: DONE v4.7 L2
- S114/S115/S116: DONE v4.6 L2
- S111/S112/S113: DONE v4.5 · S108–S110: DONE v4.4 · S105–S107: DONE v4.3
- S45: FAIL+GAP · S44: INVALID
