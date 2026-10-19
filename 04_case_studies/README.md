# ④ 问题定位实例分析

> 流程以 [02](../02_problem_localization/README.md) 为准。  
> **Ownership：** 公开本目录 = README + **15 短教学例** + 薄 stub；分析全文 / FE / runs 权威 = `runtime-guard-test/docs/`（索引 `README-anomaly-analysis.md`）。

## 15 教学例

| ID | 文件 | 课（一句话） |
|----|------|--------------|
| S01 | [examples/S01_kv-skip-zero-gap.md](./examples/S01_kv-skip-zero-gap.md) | GAP：有限垃圾，`logits_finite` 漏 |
| S10′ | [examples/S10p_fullattn-recycle-zero.md](./examples/S10p_fullattn-recycle-zero.md) | PASS recycle；对照 S01 |
| S11 | [examples/S11_mla-rope-pad-tail.md](./examples/S11_mla-rope-pad-tail.md) | MLA pad-tail ≠ recycle |
| S07 | [examples/S07_w8a8-scale-collapse-gap.md](./examples/S07_w8a8-scale-collapse-gap.md) | GAP：quant scale collapse |
| S23 | [examples/S23_weight-zero-l1.md](./examples/S23_weight-zero-l1.md) | L1-only：能检不定界 |
| S45 | [examples/S45_topk-neg-logits-gap.md](./examples/S45_topk-neg-logits-gap.md) | GAP：unique garbage |
| S43 | [examples/S43_embed-scale-blowup.md](./examples/S43_embed-scale-blowup.md) | PASS embed×100；对照 S45 |
| S22 | [examples/S22_spec-resample-salt.md](./examples/S22_spec-resample-salt.md) | `spec_acceptance` 分布课 |
| S06 | [examples/S06_moe-topk-zero.md](./examples/S06_moe-topk-zero.md) | 唯一公开 MoE 模版 |
| S26 | [examples/S26_rmsnorm-fp32-mul.md](./examples/S26_rmsnorm-fp32-mul.md) | PR-rooted RMSNorm |
| S25 | [examples/S25_rope-half-drop.md](./examples/S25_rope-half-drop.md) | PR-rooted RoPE |
| S50 | [examples/S50_swiglu-half-swap.md](./examples/S50_swiglu-half-swap.md) | SwiGLU → `logits_finite` |
| S48 | [examples/S48_residual-negate.md](./examples/S48_residual-negate.md) | Residual 极性 → bang |
| S47 | [examples/S47_attn-qkv-out.md](./examples/S47_attn-qkv-out.md) | Attn 算子 L2 |
| S33 | [examples/S33_overflow-softcap.md](./examples/S33_overflow-softcap.md) | overflow / bang |

`S10′` 公开文件名 **`S10p_`**；FE 目录为 `fail-evidence/S10/`。

## stub → 内部仓

下列同名文件仅为入口；全文在 `runtime-guard-test/docs/`（需权限）。

| stub | 内部路径 |
|------|----------|
| [anomaly-PRINCIPLES.md](./anomaly-PRINCIPLES.md) | `docs/anomaly-PRINCIPLES.md` |
| [typical-cases-keep-set-…](./typical-cases-keep-set-20261019.md) | `docs/typical-cases-keep-set-20261019.md` |
| [typical-cases-reorg-done-…](./typical-cases-reorg-done-20261019.md) | `docs/typical-cases-reorg-done-20261019.md` |
| [anomaly-skills-capability-…](./anomaly-skills-capability-20261017.md) | `docs/anomaly-skills-capability-20261017.md` |
| [anomaly-skills-verify-loop-…](./anomaly-skills-verify-loop-20261017.md) | `docs/anomaly-skills-verify-loop-20261017.md` |
| [anomaly-mining-policy-…](./anomaly-mining-policy-pr-rooted-20261018.md) | `docs/anomaly-mining-policy-pr-rooted-20261018.md` |
| [guard-skills-evaluation-pr-weighted-…](./guard-skills-evaluation-pr-weighted-20261018.md) | `docs/guard-skills-evaluation-pr-weighted-20261018.md` |
| [guard-skills-evaluation-…](./guard-skills-evaluation-20261017.md) | `docs/guard-skills-evaluation-20261017.md` |
| [guard-effectiveness-weighted-score-…](./guard-effectiveness-weighted-score-20261018.md) | `docs/guard-effectiveness-weighted-score-20261018.md` |
| [anomaly-skills-analysis-…](./anomaly-skills-analysis-20261017.md) | `docs/anomaly-skills-analysis-20261017.md` |
| [anomaly-analysis-docs-audit-…](./anomaly-analysis-docs-audit-20261018.md) | `docs/anomaly-analysis-docs-audit-20261018.md` |
| [anomaly-skills-handoff.md](./anomaly-skills-handoff.md) | `docs/anomaly-skills-handoff.md` |
| [anomaly-repro-status-…](./anomaly-repro-status-20261016.md) | `docs/anomaly-repro-status-20261016.md` |
| [anomaly-s29-s31-…](./anomaly-s29-s31-older-pr-wave2-20261017.md) | `docs/anomaly-s29-s31-older-pr-wave2-20261017.md` |
| [case-studies-runs-archive-proposal-…](./case-studies-runs-archive-proposal-20261019.md) | `docs/case-studies-runs-archive-proposal-20261019.md` |
| ~~anomaly-skills-runs/~~ | **仅** `docs/anomaly-skills-runs/` |

Skills：[06](../06_agent_skills/)（**v5.8**）· [VERIFY_HANDOFF](../06_agent_skills/VERIFY_HANDOFF.md)。
