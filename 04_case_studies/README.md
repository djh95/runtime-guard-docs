# ④ 问题定位实例分析

定位流程以 [02 问题定位](../02_problem_localization/README.md) 为准。

这里放的是**对外保留的 15 个典型案例**：每个案例自己一套材料。

每个案例只有：

- **`README.md`**：一篇讲完五条（现象 → 根因 → Guard 结果 → 复现 → 学完能做什么）
- **`evidence/`**：样本、三层计数、WHY、overlay 摘录等证据

## 名词怎么读（先看这里）

| 说法 | 含义 |
|------|------|
| **PASS** | 异常按预期出现，且期望的 detector **命中**（有 report）。 |
| **FAIL** | 未达到 PASS 的总称（复现没出来，或复现出来了但没检出，都算 FAIL）。 |
| **GAP** | **检测能力缺口**这种问题类型（例如只抓 NaN、抓不住有限乱码）。是缺口分类，不是单独一种「跑失败」标签。 |
| **FAIL+GAP** | 结论标签：异常（或目标坏输出）**已经出现**，但 detector **没检出**——既记未过关（FAIL），又标成检测缺口（GAP）。**有异常是前提**；没有异常出现时不要写 FAIL+GAP。 |
| **复现失败** | 打了 patch / overlay，但目标异常**没有出现**。不要写 GAP。结论记 **FAIL**，并注明原因（形态不对、注入未打中、负载不够、patch 未真正生效等）。可简称 **FAIL（复现未出现）** / **repro-blocked**。 |
| **结论** | 写在案例上的判定标签（PASS / FAIL+GAP / FAIL（复现未出现）等），标明是否按预期复现并检出。 |
| **样本** | 保存的请求 / 回复证据；应含 prompt + 输出，用来核对坏没坏、是否误判。 |
| **三层计数** | **trigger**（注入路径打中次数）/ **precision**（输出被判异常的次数，≠ 模型精度）/ **detect**（Guard 报告命中次数）。三者不相等；见各包 `layers.json` 等。 |
| **WHY**（`WHY_PASS` / `WHY_UNDETECTED` 等） | 对本案例结果的简短说明：为什么过关，或为什么没检出 / 没复现。 |
| **overlay 摘录** | 制造异常用的代码补丁（节选）；完整补丁在 evidence 里，摘录方便快速看改了哪。 |
| **学完能做什么** | 读完本案例，你应能掌握的具体本事——例如怎样搭出这类异常环境、怎样判断 Guard 是否漏检、或怎样把两个案例对照着做根因 / 检测分析。 |
| **origin-faithful** | 复现要忠于原 bug 逻辑；禁止用强制写 NaN、填复读 token 等方式「伪造症状」。 |
| **hybrid / 量化 KV** | 混合或量化的 KV 页语义；和稠密 bf16 不是同一套前提（S01 尤其重要）。 |

## 对外保留的 15 个典型案例

| ID | 包 | 结论 | 学完能做什么 |
|----|-----|----------|--------------|
| S01 | [cases/S01/](./cases/S01/) | FAIL+GAP | 会判断这类漏检：logits（采样前的分值）始终是有限数，没有 NaN/Inf；文字仍可能是乱码，故 `logits_finite` 漏检。能对照样本核对，并与 S10′ 对照同族脏读。 |
| S10′ | [cases/S10p/](./cases/S10p/) | PASS | 会对照 S01 做分析：同属 KV 脏读时，能说明 FullAttn 回收块未清零为何能被 `token_repeat` 抓住。 |
| S11 | [cases/S11/](./cases/S11/) | PASS | 会区分 MLA pad-tail 错位与回收块未清零：同一类 detector 命中时，仍能把根因说清楚。 |
| S07 | [cases/S07/](./cases/S07/) | FAIL+GAP | 会判断跨请求相同的真实混合脚本乱码漏检：logits（采样前的分值）始终是有限数，没有 NaN/Inf；文字仍是乱码，故 `logits_finite` 漏检。能用样本确认坏输出。 |
| S23 | [cases/S23/](./cases/S23/) | PASS | 会核对权重置零故障检出到哪一层：知道有 report，也知道 skills 还定界不到具体元素。 |
| S45 | [cases/S45/](./cases/S45/) | FAIL+GAP | 会判断各不相同的乱码漏检：logits（采样前的分值）始终是有限数，没有 NaN/Inf；文字仍是乱码，故 `logits_finite` 等漏检。能说明 top-k 打在 −logits 上，并与 S43 对照。 |
| S43 | [cases/S43/](./cases/S43/) | PASS | 会对照 S45 做分析：能说明 embedding ×100 的换行塌缩为何能被 `token_repeat` 抓住。 |
| S22 | [cases/S22/](./cases/S22/) | PASS | 会为 Spec 路径搭对检测：用 `spec_acceptance` 看分布（只看 logits 是否有限、或是否复读，不够）。 |
| S06 | [cases/S06/](./cases/S06/) | PASS | 会用本案例搭 MoE 路由类异常环境，并明白「KV 数值看起来正常」也不能据此排除 MoE 问题。 |
| S26 | [cases/S26/](./cases/S26/) | PASS | 会按 160 配方搭 RMSNorm 错乘环境：先对齐 48 并发短英文河名句，再谈 PASS / FAIL。 |
| S25 | [cases/S25/](./cases/S25/) | PASS | 会按 160 配方搭 RoPE 后半维丢失环境：对齐并发河名句与 threshold，避免只有 trigger、没有目标特征就下结论。 |
| S50 | [cases/S50/](./cases/S50/) | PASS | 会搭 SwiGLU gate/up 对调环境，并核对其会打出 `!!!!` / 出现 NaN·Inf，从而被 `logits_finite` 抓住。 |
| S48 | [cases/S48/](./cases/S48/) | PASS | 会区分 residual 极性取反与 residual-drop：能说明为何前者会打出 `!!!!` 并走到 NaN/Inf 路径。 |
| S47 | [cases/S47/](./cases/S47/) | PASS | 会搭 Attention 前 K/V 对调这一类 Attn L2 异常，并核对其可被 `token_repeat` 抓住。 |
| S33 | [cases/S33/](./cases/S33/) | PASS | 会正确做 incomplete softcap 的双树写入（Ascend + vllm），避免只打一侧导致补丁失败。 |

`S10′` 在仓库里的目录名是 **`S10p`**。相关 Skills 见 [06](../06_agent_skills/)（**v5.8**）。

## 样本字段

`evidence/` 里的样本 JSON 使用：

```json
{
  "prompt": "请求原文",
  "completion": "模型输出文本",
  "api_response": { }
}
```

`api_response` 是原始 `/v1/completions` 响应（可选但建议保留）。只看 `completion` 不够——对照时要连 prompt 一起看。
