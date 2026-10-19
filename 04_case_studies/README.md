# ④ 问题定位实例分析

> 流程与能力边界以 [02_problem_localization.md](../02_problem_localization/README.md) 为准。  
> **公开目录策略（2026-10-19）：** 只保留 **15 个典型模版** + 分析/政策文档。  
> 满量 skills-run 痕迹（S01–S152）在 **`runtime-guard-test/docs/anomaly-skills-runs/`**；原始 FE 在 **`runtime-guard-test/tests/build-anomaly-env/fail-evidence/`**。  
> Keep 清单：[`typical-cases-keep-set-20261019.md`](./typical-cases-keep-set-20261019.md)

## 典型模版（15）

| ID | 文件 | Type | 课 |
|----|------|------|-----|
| S01 | [examples/S01_kv-skip-zero-gap.md](./examples/S01_kv-skip-zero-gap.md) | KV·PD | GAP 有限垃圾 |
| S10′ | [examples/S10p_fullattn-recycle-zero.md](./examples/S10p_fullattn-recycle-zero.md) | KV·PD | PASS recycle（对照 S01） |
| S11 | [examples/S11_mla-rope-pad-tail.md](./examples/S11_mla-rope-pad-tail.md) | KV·PD | MLA pad-tail |
| S07 | [examples/S07_w8a8-scale-collapse-gap.md](./examples/S07_w8a8-scale-collapse-gap.md) | Quant | GAP scale collapse |
| S23 | [examples/S23_weight-zero-l1.md](./examples/S23_weight-zero-l1.md) | Quant | L1-only 权重 |
| S45 | [examples/S45_topk-neg-logits-gap.md](./examples/S45_topk-neg-logits-gap.md) | Embed/sampler | GAP unique garbage |
| S43 | [examples/S43_embed-scale-blowup.md](./examples/S43_embed-scale-blowup.md) | Embed/sampler | PASS embed×100 |
| S22 | [examples/S22_spec-resample-salt.md](./examples/S22_spec-resample-salt.md) | Spec | `spec_acceptance` |
| S06 | [examples/S06_moe-topk-zero.md](./examples/S06_moe-topk-zero.md) | MoE | 路由 L2（唯一 MoE 模版） |
| S26 | [examples/S26_rmsnorm-fp32-mul.md](./examples/S26_rmsnorm-fp32-mul.md) | RMSNorm | PR-rooted soft-inv |
| S25 | [examples/S25_rope-half-drop.md](./examples/S25_rope-half-drop.md) | RoPE | PR-rooted soft-inv |
| S50 | [examples/S50_swiglu-half-swap.md](./examples/S50_swiglu-half-swap.md) | SwiGLU | 算子 L2 |
| S48 | [examples/S48_residual-negate.md](./examples/S48_residual-negate.md) | Residual | 极性 → finite |
| S47 | [examples/S47_attn-qkv-out.md](./examples/S47_attn-qkv-out.md) | Attn | 算子 L2 |
| S33 | [examples/S33_overflow-softcap.md](./examples/S33_overflow-softcap.md) | Overflow | bang/overflow |

`S10′` 公开文件名用 **`S10p_`**；test 证据目录为 `fail-evidence/S10/`。

## 分析 / 政策 / 评估文档

| 编号 | 文档 | 备注 |
|------|------|------|
| A1 | [anomaly-skills-capability-20261017.md](./anomaly-skills-capability-20261017.md) | 全量能力矩阵 |
| A2 | [anomaly-skills-verify-loop-20261017.md](./anomaly-skills-verify-loop-20261017.md) | analyze→re-verify |
| A3 | [anomaly-skills-handoff.md](./anomaly-skills-handoff.md) | 160↔skills inbox |
| A4 | [anomaly-skills-analysis-20261017.md](./anomaly-skills-analysis-20261017.md) | 分析纪要 |
| A5 | ~~anomaly-skills-runs/~~ | **已迁出** → test-repo `docs/anomaly-skills-runs/` |
| A6 | [guard-skills-evaluation-pr-weighted-20261018.md](./guard-skills-evaluation-pr-weighted-20261018.md) | PR-weighted 评估 |
| A7 | [anomaly-mining-policy-pr-rooted-20261018.md](./anomaly-mining-policy-pr-rooted-20261018.md) | PR-rooted mining |
| A8 | [guard-skills-evaluation-20261017.md](./guard-skills-evaluation-20261017.md) | raw 附录 |
| A9 | [guard-effectiveness-weighted-score-20261018.md](./guard-effectiveness-weighted-score-20261018.md) | Guard 作用分 ≈0.53 |
| A10 | [anomaly-analysis-docs-audit-20261018.md](./anomaly-analysis-docs-audit-20261018.md) | 文档完备性审计 |
| A11 | [typical-cases-keep-set-20261019.md](./typical-cases-keep-set-20261019.md) | keep-set 选型 |
| A12 | [case-studies-runs-archive-proposal-20261019.md](./case-studies-runs-archive-proposal-20261019.md) | runs 迁出提案 |
| — | [anomaly-PRINCIPLES.md](./anomaly-PRINCIPLES.md) | origin-faithful 协议 |
| — | [anomaly-repro-status-20261016.md](./anomaly-repro-status-20261016.md) | 状态快照 |
| — | [anomaly-s29-s31-older-pr-wave2-20261017.md](./anomaly-s29-s31-older-pr-wave2-20261017.md) | 小波笔记 |

Skill 手册：[06_agent_skills/](../06_agent_skills/)（v5.8）。  
Skills 离线复核 handoff（15 keep-set）：[../06_agent_skills/VERIFY_HANDOFF.md](../06_agent_skills/VERIFY_HANDOFF.md)。

## 写作模板（若新增人类案例）

建议文件名：`YYYYMMDD_<short_title>.md` 或 `examples/Sxx_<short>.md`。结构：元信息 → 现象 → Guard 配置 → 抓取 → 定界（注明非 L4）→ 证据路径（test）→ 后续。
