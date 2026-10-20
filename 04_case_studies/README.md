# ④ 问题定位实例分析

> 流程以 [02](../02_problem_localization/README.md) 为准。  
> **Ownership：** 公开本目录 = README + **`cases/Sxx/` 完整包**。  
> 满量 FE / runs / 大矩阵只在私有 `runtime-guard-test`（本仓**不**放「见 test」空壳页）。

## Keep-set 完整个案包（15）

| ID | 包 | 结果（归档） | 课（一句话） |
|----|-----|--------------|--------------|
| S01 | [cases/S01/](./cases/S01/) | FAIL+GAP | 有限垃圾，`logits_finite` 漏 |
| S10′ | [cases/S10p/](./cases/S10p/) | PASS | FullAttn recycle；对照 S01 |
| S11 | [cases/S11/](./cases/S11/) | PASS | MLA pad-tail ≠ recycle |
| S07 | [cases/S07/](./cases/S07/) | FAIL+GAP | W8A8 scale collapse 汤 |
| S23 | [cases/S23/](./cases/S23/) | PASS | L1-only：能检不定界 |
| S45 | [cases/S45/](./cases/S45/) | FAIL+GAP | unique garbage |
| S43 | [cases/S43/](./cases/S43/) | PASS | embed×100；对照 S45 |
| S22 | [cases/S22/](./cases/S22/) | PASS | `spec_acceptance` 分布课 |
| S06 | [cases/S06/](./cases/S06/) | PASS | 唯一公开 MoE 模版 |
| S26 | [cases/S26/](./cases/S26/) | PASS | PR-rooted RMSNorm |
| S25 | [cases/S25/](./cases/S25/) | PASS | PR-rooted RoPE half-drop |
| S50 | [cases/S50/](./cases/S50/) | PASS | SwiGLU → `logits_finite` |
| S48 | [cases/S48/](./cases/S48/) | PASS | Residual 极性 → bang |
| S47 | [cases/S47/](./cases/S47/) | PASS | Attn K/V swap L2 |
| S33 | [cases/S33/](./cases/S33/) | PASS | incomplete softcap |

每包 = external five-bar（现象→根因→Guard→复现→课）+ `evidence/`。

`S10′` 目录名 **`S10p`**。Skills：[06](../06_agent_skills/)（**v5.8**）。
