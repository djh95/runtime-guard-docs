# Anomaly skills handoff (watcher)

**Rev:** `2026-10-17T1420+08` — **S34 + S35 skills done** (v1.9).  
Prior: S32/S33 v1.8; S29–S31 v1.7.

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
| PASS | S06, S08, S10′, S11, S12, S14, S16–S19, S20, S22–S26, S28–**S35** |
| FAIL+GAP | S01, S07 |
| Parked | S02/S03/S05/S09 HARD; S04 HCCN-blocked; S13 BLOCKED; S15 skip; S21 HARD (trig=0); **S27 BLOCKED** |
| **Builder** | check open set (S21 / etc.) — skills on **162** |

## Inbox (160 → skills)

- **S35 PASS** `136/46/48` token_repeat | evidence `fail-evidence/S35/` | causal-off future leak; ≠ S34
  - **skills done** 2026-10-17: full loop; skills **v1.9** L2; note `docs/anomaly-skills-runs/S35-20261017.md`
- **S34 PASS** `18/26/48` token_repeat | evidence `fail-evidence/S34/` | attn scale drop 1/sqrt(d)→1.0; ≠ S20/S32/S33
  - **skills done** 2026-10-17: full loop; skills **v1.9** L2; note `docs/anomaly-skills-runs/S34-20261017.md`

### Prior (skills done)

- **S33/S32** | **skills done** v1.8
- **S31/S30/S29** | **skills done** v1.7
- **S28/S26/S25** | **skills done** v1.6
- **S24/S23/S22/S20** | **skills done** v1.5–v1.3

## Blocked note (not Inbox)

- **S27 BLOCKED** — pe-presliced MLA no-op. Skills skipped.

## Requests → Build-on-160

Living capability: [anomaly-skills-capability-20261017.md](anomaly-skills-capability-20261017.md).

Skills: watching for next PENDING. Builder open set as available.

## Skills verify (2026-10-17)

- S32/S33: **v1.8**
- S34/S35: **v1.9** — `docs/anomaly-skills-runs/S3{4,5}-20261017.md`
