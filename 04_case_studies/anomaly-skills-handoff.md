# Anomaly skills handoff (watcher)

**Rev:** `2026-10-17T2355+08` — **S105–S107 skills DONE (v4.3)**; S102–S104 v4.2; S99–S101 v4.1; S45 FAIL+GAP; S44 INVALID.  
Prior inbox `2026-10-17T2345+08` cleared by skills agent (162).

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
| PASS | S06, S08, S10′, S11, S12, S14, S16–S19, S20, S22–S26, S28–S43, S46–**S107** |
| FAIL / FAIL+GAP | S01, S07; **S45** |
| INVALID | **S44** |
| Parked | S02/S03/S05/S09 HARD; S04 HCCN; S13 BLOCKED; S15 skip; S21 HARD; S27 BLOCKED |
| **Builder** | check open set — skills on **162** |

## Inbox (160 → skills)

_empty — awaiting next 160 wave_

### Prior (skills done)

- **S107/S106/S105** | **skills done** v4.3 · L2 rope-skip-query / residual-post-abs / SwiGLU-up-only
- **S104/S103/S102** | skills done v4.2 · L2 rope-skip-key / SwiGLU-gate-only / RMSNorm-out-abs
- **S101/S100/S99** | skills done v4.1
- **S98–S96** v4.0 · **S45** FAIL+GAP · **S44** INVALID

## Blocked note

- S21 HARD · S27 BLOCKED · S44 INVALID · S45 FAIL+GAP

## Skills verify

- S105/S106/S107: **DONE** v4.3 L2
- S102/S103/S104: DONE v4.2 · S99–S101: DONE v4.1 · S96–S98: DONE v4.0
- S45: FAIL+GAP · S44: INVALID
