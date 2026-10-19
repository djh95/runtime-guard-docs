# ④ 问题定位实例分析

> 流程与能力边界以 [02_problem_localization](../02_problem_localization/README.md) 为准。  
> **公开目录策略：** 只保留 **15 个典型模版** + 短入口 stub + 必要短协议。  
> **权威分析矩阵 / verify-loop / 评估 / mining inventory / handoff 全文** 在  
> [`runtime-guard-test/docs/`](https://github.com/djh95/runtime-guard-test/tree/main/docs)  
> （索引：[README-anomaly-analysis.md](https://github.com/djh95/runtime-guard-test/blob/main/docs/README-anomaly-analysis.md)）。  
> 满量 skills-run：`runtime-guard-test/docs/anomaly-skills-runs/` · FE：`tests/build-anomaly-env/fail-evidence/`。  
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

## 本仓保留的短文档

| 文档 | 说明 |
|------|------|
| [anomaly-PRINCIPLES.md](./anomaly-PRINCIPLES.md) | origin-faithful 短协议（公开可读） |
| [typical-cases-keep-set-20261019.md](./typical-cases-keep-set-20261019.md) | 15 keep-set 选型 |
| [typical-cases-reorg-done-20261019.md](./typical-cases-reorg-done-20261019.md) | 公开 reorg 完成记录 |

## 分析 / 评估入口（stub → test 仓全文）

下列同名文件在本仓仅为 **入口 stub**；点开即跳到 test 仓权威副本。

| 入口 stub | 权威全文 |
|-----------|----------|
| [anomaly-skills-capability-…](./anomaly-skills-capability-20261017.md) | [test `docs/…`](https://github.com/djh95/runtime-guard-test/blob/main/docs/anomaly-skills-capability-20261017.md) |
| [anomaly-skills-verify-loop-…](./anomaly-skills-verify-loop-20261017.md) | [test](https://github.com/djh95/runtime-guard-test/blob/main/docs/anomaly-skills-verify-loop-20261017.md) |
| [anomaly-mining-policy-…](./anomaly-mining-policy-pr-rooted-20261018.md) | [test](https://github.com/djh95/runtime-guard-test/blob/main/docs/anomaly-mining-policy-pr-rooted-20261018.md) |
| [guard-skills-evaluation-pr-weighted-…](./guard-skills-evaluation-pr-weighted-20261018.md) | [test](https://github.com/djh95/runtime-guard-test/blob/main/docs/guard-skills-evaluation-pr-weighted-20261018.md) |
| [guard-skills-evaluation-…](./guard-skills-evaluation-20261017.md) | [test](https://github.com/djh95/runtime-guard-test/blob/main/docs/guard-skills-evaluation-20261017.md) |
| [guard-effectiveness-weighted-score-…](./guard-effectiveness-weighted-score-20261018.md) | [test](https://github.com/djh95/runtime-guard-test/blob/main/docs/guard-effectiveness-weighted-score-20261018.md) |
| [anomaly-skills-analysis-…](./anomaly-skills-analysis-20261017.md) | [test](https://github.com/djh95/runtime-guard-test/blob/main/docs/anomaly-skills-analysis-20261017.md) |
| [anomaly-analysis-docs-audit-…](./anomaly-analysis-docs-audit-20261018.md) | [test](https://github.com/djh95/runtime-guard-test/blob/main/docs/anomaly-analysis-docs-audit-20261018.md) |
| [anomaly-skills-handoff.md](./anomaly-skills-handoff.md) | [test](https://github.com/djh95/runtime-guard-test/blob/main/docs/anomaly-skills-handoff.md) |
| [anomaly-repro-status-…](./anomaly-repro-status-20261016.md) | [test](https://github.com/djh95/runtime-guard-test/blob/main/docs/anomaly-repro-status-20261016.md) |
| [anomaly-s29-s31-…](./anomaly-s29-s31-older-pr-wave2-20261017.md) | [test](https://github.com/djh95/runtime-guard-test/blob/main/docs/anomaly-s29-s31-older-pr-wave2-20261017.md) |
| [case-studies-runs-archive-proposal-…](./case-studies-runs-archive-proposal-20261019.md) | [test](https://github.com/djh95/runtime-guard-test/blob/main/docs/case-studies-runs-archive-proposal-20261019.md) |
| ~~anomaly-skills-runs/~~ | **仅** [test `docs/anomaly-skills-runs/`](https://github.com/djh95/runtime-guard-test/tree/main/docs/anomaly-skills-runs) |

Skill 手册：[06_agent_skills/](../06_agent_skills/)（**v5.8** / [SKILLS_METADATA.md](../06_agent_skills/SKILLS_METADATA.md)）。  
Skills 离线复核 handoff：[../06_agent_skills/VERIFY_HANDOFF.md](../06_agent_skills/VERIFY_HANDOFF.md)。

## 写作模板（若新增人类案例）

建议文件名：`examples/Sxx_<short>.md`。结构：元信息 → 现象 → Guard 配置 → 抓取 → 定界（注明非 L4）→ 证据路径（test）→ 后续。大体积实验日志请写到 **runtime-guard-test/docs/**，不要再塞回本目录全文。
