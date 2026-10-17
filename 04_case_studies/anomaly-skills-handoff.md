# Anomaly skills handoff (watcher)

**Rev:** `2026-10-17T1540+08` — **S39 + S40 + S41 skills done** (v2.1).  
Prior: S36–S38 v2.0; S34/S35 v1.9; S32/S33 v1.8.

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
| PASS | S06, S08, S10′, S11, S12, S14, S16–S19, S20, S22–S26, S28–**S41** |
| FAIL+GAP | S01, S07 |
| Parked | S02/S03/S05/S09 HARD; S04 HCCN-blocked; S13 BLOCKED; S15 skip; S21 HARD (trig=0); **S27 BLOCKED** |
| **Builder** | check open set — skills on **162** |

## Inbox (160 → skills)

- **S41 PASS** `58/48/48` logits_finite | evidence `fail-evidence/S41/` | post-FA attn ×1000; ≠ S34/S14/S35
  - **skills done** 2026-10-17: full loop; skills **v2.1** L2; note `docs/anomaly-skills-runs/S41-20261017.md`
- **S40 PASS** `58/45/48` token_repeat | evidence `fail-evidence/S40/` | RoPE skip unrotated Q/K; ≠ S25/S28/S37
  - **skills done** 2026-10-17: full loop; skills **v2.1** L2; note `docs/anomaly-skills-runs/S40-20261017.md`
- **S39 PASS** `58/48/48` logits_finite | evidence `fail-evidence/S39/` | SwiGLU skip-silu; ≠ S26/S31/S38
  - **skills done** 2026-10-17: full loop; skills **v2.1** L2; note `docs/anomaly-skills-runs/S39-20261017.md`

### Prior (skills done)

- **S38/S37/S36** | **skills done** v2.0
- **S35/S34** | **skills done** v1.9
- **S33/S32** | **skills done** v1.8
- **S31/S30/S29** | **skills done** v1.7
- **S28/S26/S25** | **skills done** v1.6
- **S24/S23/S22/S20** | **skills done** v1.5–v1.3

## Blocked note (not Inbox)

- **S27 BLOCKED** — pe-presliced MLA no-op. Skills skipped.
- **S21 HARD** — parked (trig=0).

## Requests → Build-on-160

Living capability: [anomaly-skills-capability-20261017.md](anomaly-skills-capability-20261017.md).

Skills: watching for next PENDING.

## Skills verify (2026-10-17)

- S36/S37/S38: **v2.0**
- S39/S40/S41: **v2.1** — `docs/anomaly-skills-runs/S3{9,40,41}-20261017.md`
