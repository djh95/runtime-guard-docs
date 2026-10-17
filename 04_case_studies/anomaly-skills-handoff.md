# Anomaly skills handoff (watcher)

**Rev:** `2026-10-17T1935+08` — **S66–S68 skills DONE (v3.0)**; S63–S65 v2.9; S60–S62 v2.8; S45 FAIL+GAP; S44 INVALID.  
Prior inbox `2026-10-17T1925+08` cleared by skills agent (162).

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
| PASS | S06, S08, S10′, S11, S12, S14, S16–S19, S20, S22–S26, S28–S43, S46–**S68** |
| FAIL / FAIL+GAP | S01, S07; **S45** |
| INVALID | **S44** |
| Parked | S02/S03/S05/S09 HARD; S04 HCCN; S13 BLOCKED; S15 skip; S21 HARD; S27 BLOCKED |
| **Builder** | check open set — skills on **162** |

## Inbox (160 → skills)

_empty — awaiting next 160 wave_

### Prior (skills done)

- **S68/S67/S66** | **skills done** v3.0 · L2 RMSNorm-weight-negate / SwiGLU-out-negate / attn-scale÷50
- **S65/S64/S63** | skills done v2.9 · L2 attn-out-negate / residual÷50 / logits×50
- **S62/S61/S60** | skills done v2.8
- **S59–S57** v2.7 · **S56–S54** v2.6 · **S53–S51** v2.5 · **S50–S48** v2.4 · **S45** FAIL+GAP · **S44** INVALID

## Blocked note

- S21 HARD · S27 BLOCKED · S44 INVALID · S45 FAIL+GAP

## Skills verify

- S66/S67/S68: **DONE** v3.0 L2
- S63/S64/S65: DONE v2.9 · S60–S62: DONE v2.8 · S57–S59: DONE v2.7
- S45: FAIL+GAP · S44: INVALID
