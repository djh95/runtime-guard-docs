# Anomaly skills handoff (watcher)

Skills agent (162) watches this file + store copy for **new PASS / FAIL+GAP** rows from the **160 builder**.

Skills live in `analysis/skill/` (**v1.6**). Offline analyze only — **do not steal 160 cards**.

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
- **S30 PASS** `2/14/48` token_repeat | 160 cards `2,3` | run `30_null_block_kv_dirt-20261017T123743` | evidence `tests/build-anomaly-env/fail-evidence/S30/` | soft-inv #39444 null-block KV dirt (ones); ≠ S01/S10/S23/S24
- **S29 PASS** `132/14/48` token_repeat | 160 cards `2,3` | run `29_logits_fp16_demote-20261017T122734` | evidence `tests/build-anomaly-env/fail-evidence/S29/` | V2 Sampler post-temp fp16 demote; ≠ S20/S26
- **S28 PASS** `462/16/48` token_repeat | 160 cards `4,5` | run `28_rope_style_flip-20261017T121429` | evidence `tests/build-anomaly-env/fail-evidence/S28/` | soft-inv #7341/#7082 force neox→interleaved; ≠ S25/S11
  - **skills done** 2026-10-17: full loop; score `phrase_repeat`; skills **v1.6** L2; note `docs/anomaly-skills-runs/S28-20261017.md`
- **S26 PASS** `470/14/48` token_repeat | 160 cards `6,7` | run `26_rmsnorm_fp32_mul-20261017T115830` | evidence `tests/build-anomaly-env/fail-evidence/S26/` | soft-inv #42379 RMSNorm fp32-mul
  - **skills done** 2026-10-17: full loop; skills **v1.6** L2 dtype class; note `docs/anomaly-skills-runs/S26-20261017.md`
- **S25 PASS** `462/15/48` token_repeat | 160 cards `4,5` | run `25_rope_siso_half_drop-20261017T115523` | evidence `tests/build-anomaly-env/fail-evidence/S25/` | soft-inv #7082 2nd-half drop; ≠ S11
  - **skills done** 2026-10-17: full loop; skills **v1.6** L2 RoPE half; note `docs/anomaly-skills-runs/S25-20261017.md`
- **S24 PASS** `2/48/48` token_repeat | evidence `fail-evidence/S24/` | **skills done** v1.5
- **S23 PASS** `2/17/48` token_repeat | evidence `fail-evidence/S23/` | **skills done** v1.5
- **S22 PASS** `130/45/48` spec_acceptance | evidence `fail-evidence/S22/` | **skills done** v1.4
- **S20 PASS** `130/48/48` token_repeat | evidence `fail-evidence/S20/` | **skills done** v1.3

## Blocked note (not Inbox)

- **S27 BLOCKED** — #6880/#6310 looked good but pe-presliced MLA makes force `rotary_dim=head_size` a no-op (trig=0); clean V2-Lite on G2 also emits zero/digit garbage without overlay. Skills skipped.

## Requests → Build-on-160

Living capability: [anomaly-skills-capability-20261017.md](anomaly-skills-capability-20261017.md).

Older-PR mine wave-2 closed (S29/S30/S31). Skills on **162**; continue watching for new Inbox rows (S29–S31 pending skills).

## Skills verify (2026-10-17)

- Batch PASS set (S06…S19 + S01/S07): no skill edit — `docs/anomaly-skills-runs/batch-pass-wave-20261017.md`
- Soft-inv wave S25/S26/S28: **v1.6** — `docs/anomaly-skills-runs/S2{5,6,8}-20261017.md`
- Wave-2 S29/S30/S31: **inbox open** for skills (sampling/cast · null-block KV · residual drop)
