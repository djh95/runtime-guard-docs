# Anomaly skills handoff (watcher)

**Rev:** `2026-10-17T1320+08` — **S32 + S33 skills done** (v1.8).  
Prior: S29–S31 v1.7; soft-inv S25/S26/S28 v1.6.

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
| PASS | S06, S08, S10′, S11, S12, S14, S16–S19, S20, S22–S26, S28–**S33** |
| FAIL+GAP | S01, S07 |
| Parked | S02/S03/S05/S09 HARD; S04 HCCN-blocked; S13 BLOCKED; S15 skip; S21 HARD (trig=0); **S27 BLOCKED** |
| **Builder** | check open set (S21 dummy / etc.) — skills on **162** |

## Inbox (160 → skills)

- **S33 PASS** `132/15/48` token_repeat | evidence `fail-evidence/S33/` | incomplete softcap; ≠ S20
  - **skills done** 2026-10-17: full loop; skills **v1.8** L2; note `docs/anomaly-skills-runs/S33-20261017.md`
- **S32 PASS** `132/47/48` token_repeat | evidence `fail-evidence/S32/` | FIA FULL-graph pad #7144; ≠ S14
  - **skills done** 2026-10-17: full loop; score `pad_echo`; skills **v1.8** L2; note `docs/anomaly-skills-runs/S32-20261017.md`

### Prior (skills done)

- **S31/S30/S29** | **skills done** v1.7
- **S28/S26/S25** | **skills done** v1.6
- **S24/S23/S22/S20** | **skills done** v1.5–v1.3

## Blocked note (not Inbox)

- **S27 BLOCKED** — pe-presliced MLA no-op. Skills skipped.

## Requests → Build-on-160

Living capability: [anomaly-skills-capability-20261017.md](anomaly-skills-capability-20261017.md).

Skills: watching for next PENDING. Builder open set as available.

## Skills verify (2026-10-17)

- Wave-2 S29/S30/S31: **v1.7**
- S32/S33: **v1.8** — `docs/anomaly-skills-runs/S3{2,3}-20261017.md`
