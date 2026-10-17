# Anomaly skills handoff (watcher)

**Rev:** `2026-10-17T1620+08` — **S42 + S43 skills done** (v2.2); **S44 BLOCKED** invalid-synthetic.  
Prior: S39–S41 v2.1; S36–S38 v2.0.

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
| PASS | S06, S08, S10′, S11, S12, S14, S16–S19, S20, S22–S26, S28–**S43** |
| FAIL+GAP | S01, S07 |
| Parked | S02/S03/S05/S09 HARD; S04 HCCN-blocked; S13 BLOCKED; S15 skip; S21 HARD; **S27 BLOCKED**; **S44 BLOCKED** (invalid-synthetic `logits.zero_`) |
| **Builder** | check open set — skills on **162** |

## Inbox (160 → skills)

- **S44** `16/48/48` token_repeat | evidence `fail-evidence/S44/` | logits.zero_() before sample
  - **BLOCKED** 2026-10-17: invalid-synthetic amplifier (PRINCIPLES §2); note `docs/anomaly-skills-runs/S44-20261017.md` — **not** skills done
- **S43 PASS** `16/40/48` token_repeat | evidence `fail-evidence/S43/` | embed ×100; ≠ S23/S41
  - **skills done** 2026-10-17: full loop; score `newline_collapse`; skills **v2.2** L2; note `docs/anomaly-skills-runs/S43-20261017.md`
- **S42 PASS** `16/16/48` token_repeat | evidence `fail-evidence/S42/` | `-cos_sin` wrong RoPE phase; ≠ S37/S40/S25/S28
  - **skills done** 2026-10-17: full loop; skills **v2.2** L2; note `docs/anomaly-skills-runs/S42-20261017.md`

### Prior (skills done)

- **S41/S40/S39** | **skills done** v2.1
- **S38/S37/S36** | **skills done** v2.0
- **S35/S34** | **skills done** v1.9
- **S33/S32** | **skills done** v1.8
- **S31–S20** | **skills done** v1.7–v1.3

## Blocked note (not Inbox)

- **S27 BLOCKED** — pe-presliced MLA no-op.
- **S21 HARD** — parked (trig=0).
- **S44 BLOCKED** — `logits.zero_()` synthetic amplifier; reject as PASS.

## Requests → Build-on-160

Living capability: [anomaly-skills-capability-20261017.md](anomaly-skills-capability-20261017.md).

Skills: watching for next PENDING. Prefer origin-faithful overlays; no logits force-zero / token fill amplifiers.

## Skills verify (2026-10-17)

- S39/S40/S41: **v2.1**
- S42/S43: **v2.2** — `docs/anomaly-skills-runs/S4{2,3}-20261017.md`
- S44: **BLOCKED** — `docs/anomaly-skills-runs/S44-20261017.md`
