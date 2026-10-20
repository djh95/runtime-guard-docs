# ④ 问题定位实例分析

定位流程以 [02 问题定位](../02_problem_localization/README.md) 为准。

这里放的是**对外保留的 15 个典型案**：每个案自己一套材料，读完即可，不必再去别的仓库找正文。

每个案只有：

- **`README.md`**：一篇讲完五条（现象 → 根因 → Guard 结果 → 复现 → 教学要点）
- **`evidence/`**：样本、三层计数、WHY、overlay 摘录等证据

更大量的历史跑数、原始日志不在本仓。

## 名词怎么读（先看这里）

| 说法 | 含义 |
|------|------|
| **PASS** | 异常按 origin 复现出来了，并且期望的 detector **命中**（有 report）。 |
| **FAIL+GAP** | 异常（或 precision）已经出现，但现有 detector **没抓住**——说明产品侧有检测缺口，不是「没跑 overlay」。 |
| **FAIL** | 归档结果失败；若同时写 GAP，重点看缺口类型（常见：有限垃圾漏检）。 |
| **GAP** | 检测器能力缺口。例如输出是有限乱码，而 `logits_finite` 只抓 NaN/Inf。 |
| **trigger / precision / detect** | 三层计数：路径是否打中（trigger）→ 是否出现异常输出（precision）→ Guard 是否报警（detect）。三者不相等。 |
| **教学要点** | 读完这个案，你应带走的判断标准或对照关系（表里这一列）。不是课堂作业，也不是内部黑话。 |
| **origin-faithful** | 复现要忠于原 bug 逻辑；禁止用强制写 NaN、填复读 token 等方式「伪造症状」。 |
| **hybrid / 量化 KV** | 混合或量化的 KV 页语义；和稠密 bf16 不是同一套前提（S01 尤其重要）。 |

## 对外保留的 15 个典型案

| ID | 包 | 归档结果 | 教学要点 |
|----|-----|----------|----------|
| S01 | [cases/S01/](./cases/S01/) | FAIL+GAP | 输出可以全程有限却仍是乱码；`logits_finite` 抓不住，这是 detector 缺口。 |
| S10′ | [cases/S10p/](./cases/S10p/) | PASS | 同属 KV 脏读：FullAttn 回收块未清零能被 `token_repeat` 抓住；对照 S01 漏检。 |
| S11 | [cases/S11/](./cases/S11/) | PASS | MLA 的 pad-tail 错位 ≠ 回收块未清零；同一类 detector，根因不同。 |
| S07 | [cases/S07/](./cases/S07/) | FAIL+GAP | W8A8 scale 崩溃会打出**真实的混合脚本乱码**，且跨请求相同；`logits_finite` 仍漏检。 |
| S23 | [cases/S23/](./cases/S23/) | PASS | 能检出权重置零故障，但 skills 定界不到具体元素（L1-only）。 |
| S45 | [cases/S45/](./cases/S45/) | FAIL+GAP | top-k 作用在 −logits 上会产生各不相同的有限乱码；现有 detector 双双 miss。 |
| S43 | [cases/S43/](./cases/S43/) | PASS | embedding ×100 导致换行塌缩，能被 `token_repeat` 抓住；对照 S45。 |
| S22 | [cases/S22/](./cases/S22/) | PASS | Spec 路径要用 `spec_acceptance` 看分布，不能只用有限/复读阈值硬套。 |
| S06 | [cases/S06/](./cases/S06/) | PASS | 对外保留案里唯一 MoE 路由模版；KV 有限不等于 MoE 问题已排除。 |
| S26 | [cases/S26/](./cases/S26/) | PASS | PR-rooted RMSNorm（fp32 错乘）；160 成功靠 48 并发短英文河名句。 |
| S25 | [cases/S25/](./cases/S25/) | PASS | PR-rooted RoPE 后半维丢失；负载配方必须与 160 对齐，否则只有 trigger 没有目标特征。 |
| S50 | [cases/S50/](./cases/S50/) | PASS | SwiGLU gate/up 对调会走到 bang / 非有限，可被 `logits_finite` 抓住。 |
| S48 | [cases/S48/](./cases/S48/) | PASS | Residual 极性取反 → `!!!!`；与 residual-drop 要分开看。 |
| S47 | [cases/S47/](./cases/S47/) | PASS | Attention 前 K/V 对调是对外保留案里的 Attn L2 代表。 |
| S33 | [cases/S33/](./cases/S33/) | PASS | incomplete softcap（跳过 `*cap`）；overlay **必须双树写入**（Ascend + vllm）。 |

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
