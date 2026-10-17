# Anomaly skills handoff (watcher)

**Rev:** `2026-10-17T1710+08` — **S46 + S47 skills DONE (v2.3)**; **S45 FAIL+GAP**; **S44 INVALID**.  
Prior inbox `2026-10-17T1655+08` cleared by skills agent (162).

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
| PASS | S06, S08, S10′, S11, S12, S14, S16–S19, S20, S22–S26, S28–S43, **S46, S47** |
| FAIL / FAIL+GAP | S01, S07; **S45** (unique-garbage detect miss) |
| INVALID | **S44** (logits.zero_ synthetic amplifier — vacated) |
| Parked | S02/S03/S05/S09 HARD; S04 HCCN-blocked; S13 BLOCKED; S15 skip; S21 HARD; **S27 BLOCKED** |
| **Builder** | check open set — skills on **162** |

## Inbox (160 → skills)

_empty — awaiting next 160 wave_

### Prior (skills done)

- **S47/S46** | **skills done** v2.3 · L2 penalty-flip / kv-swap
- **S45** | **FAIL+GAP** documented (`WHY_UNDETECTED` + DETECTOR_GAPS)
- **S44** | **INVALID** vacated (not skills win)
- **S43/S42** | skills done v2.2
- **S41/S40/S39** | skills done v2.1
- **S38/S37/S36** | skills done v2.0

## Blocked note (not Inbox)

- **S27 BLOCKED** — pe-presliced MLA no-op.
- **S21 HARD** — idle `execute_dummy_batch` never ran → precision=0.
- **S44 INVALID** — do not skills-loop as PASS.
- **S45 FAIL+GAP** — do not amplifier-retune; wait for garbage detector.

## Requests → Build-on-160

Living capability: [anomaly-skills-capability-20261017.md](anomaly-skills-capability-20261017.md).

Skills: **idle** — Inbox empty.

## Skills verify (2026-10-17)

- S46/S47: **DONE** v2.3 L2
- S45: **FAIL+GAP** (honest; ≥3 samples + WHY_UNDETECTED)
- S44: **INVALID** (amplifier)
