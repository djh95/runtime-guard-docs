# ④ 问题定位实例分析

> 流程以 [02](../02_problem_localization/README.md) 为准。  
> **Ownership：** 公开本目录 = README + **15 短教学例** + **完整个案包**（目前 `cases/S01/`）。  
> 满量 FE / runs / 大体积分析矩阵只在私有 `runtime-guard-test`（本仓**不**再放「见 test」空壳页）。

## 15 教学例

| ID | 文件 | 课（一句话） |
|----|------|--------------|
| S01 | [examples/S01_kv-skip-zero-gap.md](./examples/S01_kv-skip-zero-gap.md) · **[cases/S01/](./cases/S01/)** | GAP：有限垃圾，`logits_finite` 漏 |
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

`S10′` 公开文件名 **`S10p_`**。

## 完整个案包

| ID | 路径 | 说明 |
|----|------|------|
| S01 | [cases/S01/](./cases/S01/) | External five-bar：现象→根因→Guard GAP→复现 Then/Now→课；含 `evidence/` |

Skills：[06](../06_agent_skills/)（**v5.8**）· [VERIFY_HANDOFF](../06_agent_skills/VERIFY_HANDOFF.md)。
