# Anomaly skills handoff (watcher)

Skills agent (162) watches this file + store copy for **new PASS / FAIL+GAP** rows from the **160 builder**.

Skills live in `analysis/skill/` (**v1.7**). Offline analyze only — **do not steal 160 cards**.

```bash
export RG_TEST=/path/to/runtime-guard-test
PYTHONPATH="$RG_TEST" python -m analysis.scripts.summarize_reports --report-dir <report>
PYTHONPATH="$RG_TEST" python -m analysis.scripts.score_completion_samples --sample-dir <samples>
PYTHONPATH="$RG_TEST" python -m analysis.scripts.verify_request_kv --report <r.json> --kv-dir <rank_dir>
```

## Current baseline (do not rebuild on 160)

| Bucket | IDs |
|--------|-----|
| PASS | S06, S08, S10′, S11, S12, S14, S16–S19, S20, S22–S26, S28–**S31** |
| FAIL+GAP | S01, S07 |
| Parked | S02/S03/S05/S09 HARD; S04 HCCN-blocked; S13 BLOCKED; S15 skip; S21 HARD (trig=0); **S27 BLOCKED** |
| **Builder** | **IDLE** after older-PR wave-2 (S29/S30/S31) — skills on **162** |

## Inbox (160 → skills)

- **S31 PASS** `470/48/48` token_repeat | 160 cards `12,13` | run `31_residual_drop-20261017T124734` | evidence `tests/build-anomaly-env/fail-evidence/S31/` | AscendRMSNorm skip residual accumulate; ≠ S26
  - **skills done** 2026-10-17: full loop; skills **v1.7** L2 residual-drop; note `docs/anomaly-skills-runs/S31-20261017.md`
- **S30 PASS** `2/14/48` token_repeat | 160 cards `2,3` | run `30_null_block_kv_dirt-20261017T123743` | evidence `tests/build-anomaly-env/fail-evidence/S30/` | soft-inv #39444 null-block KV dirt; ≠ S01/S10/S23/S24
  - **skills done** 2026-10-17: full loop; skills **v1.7** L2; note `docs/anomaly-skills-runs/S30-20261017.md`
- **S29 PASS** `132/14/48` token_repeat | 160 cards `2,3` | run `29_logits_fp16_demote-20261017T122734` | evidence `tests/build-anomaly-env/fail-evidence/S29/` | V2 Sampler post-temp fp16 demote; ≠ S20/S26
  - **skills done** 2026-10-17: full loop; skills **v1.7** L2 cast; note `docs/anomaly-skills-runs/S29-20261017.md`
- **S28 PASS** `462/16/48` token_repeat | evidence `fail-evidence/S28/` | **skills done** v1.6
- **S26 PASS** `470/14/48` token_repeat | evidence `fail-evidence/S26/` | **skills done** v1.6
- **S25 PASS** `462/15/48` token_repeat | evidence `fail-evidence/S25/` | **skills done** v1.6
- **S24/S23/S22/S20** | **skills done** v1.5–v1.3

## Blocked note (not Inbox)

- **S27 BLOCKED** — pe-presliced MLA no-op + dirty clean V2-Lite. Skills skipped.

## Requests → Build-on-160

Living capability: [anomaly-skills-capability-20261017.md](anomaly-skills-capability-20261017.md).

Older-PR mine wave-2 closed. Skills on **162**; continue watching for new Inbox rows.

## Skills verify (2026-10-17)

- Soft-inv S25/S26/S28: **v1.6**
- Wave-2 S29/S30/S31: **v1.7** — `docs/anomaly-skills-runs/S2{9,30,31}-20261017.md`
