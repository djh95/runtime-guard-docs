# ④ 问题定位实例分析

定位流程以 [02 问题定位](../02_problem_localization/README.md) 为准。

这里放的是**对外保留的 15 个典型案例**：每个案例自己一套材料。

每个案例只有：

- **`README.md`**：一篇讲完（现象 → 根因 → Guard 结果 → 复现 → 别人按包能核对什么）
- **`evidence/`**：样本、三层计数、WHY、overlay 摘录等证据

## 名词怎么读（先看这里）

| 说法 | 含义 |
|------|------|
| **PASS** | 异常按预期出现，且期望的 detector **命中**（有 report）。 |
| **FAIL** | 未达到 PASS 的总称（复现没出来，或复现出来了但没检出，都算 FAIL）。 |
| **GAP** | **检测能力缺口**这种问题类型（例如只抓 NaN、抓不住有限乱码）。是缺口分类，不是单独一种「跑失败」标签。 |
| **FAIL+GAP** | 结论标签：异常（或目标坏输出）**已经出现**，但 detector **没检出**——既记未过关（FAIL），又标成检测缺口（GAP）。**有异常是前提**；没有异常出现时不要写 FAIL+GAP。 |
| **复现失败** | 打了 patch / overlay，但目标异常**没有出现**。不要写 GAP。结论记 **FAIL**，并注明原因（形态不对、注入未打中、负载不够、patch 未真正生效等）。可简称 **FAIL（复现未出现）** / **repro-blocked**。 |
| **结案结论** | 写在案例上的判定标签（PASS / FAIL+GAP / FAIL（复现未出现）等），标明是否按预期复现并检出。 |
| **样本** | 保存的请求 / 回复证据；应含 prompt + 输出，用来核对坏没坏、是否误判。 |
| **三层计数** | **trigger**（注入路径打中次数）/ **precision**（输出被判异常的次数，≠ 模型精度）/ **detect**（Guard 报告命中次数）。三者不相等；见各包 `layers.json` 等。 |
| **WHY**（`WHY_PASS` / `WHY_UNDETECTED` 等） | 对本案例结果的简短说明：为什么过关，或为什么没检出 / 没复现。 |
| **overlay 摘录** | 制造异常用的代码补丁（节选）；完整补丁在 evidence 里，摘录方便快速看改了哪。 |
| **origin-faithful** | 复现要忠于原 bug 逻辑；禁止用强制写 NaN、填复读 token 等方式「伪造症状」。 |
| **hybrid / 量化 KV** | 混合或量化的 KV 页语义；和稠密 bf16 不是同一套前提（S01 尤其重要）。 |

## 对外保留的 15 个典型案例

| ID | 包 | 结案结论 | 根因 | 现象 | 检测器 | trigger / precision / detect |
|----|-----|----------|------|------|--------|------------------------------|
| S01 | [cases/S01/](./cases/S01/) | FAIL+GAP | KV 新块未置零→脏读 | 文字乱码嫌疑 | 期望 `logits_finite`→未检出；乱码检测漏检 | 136 / 25 / 0 |
| S10′ | [cases/S10p/](./cases/S10p/) | PASS | FullAttn 回收块未清零 | 复读 / `xxxx` 塌缩 | `token_repeat` | 65 / 20 / 79 |
| S11 | [cases/S11/](./cases/S11/) | PASS | MLA RoPE pad-tail 错位 | digit / collapse 垃圾 | `token_repeat` | 138 / 39 / 60 |
| S07 | [cases/S07/](./cases/S07/) | FAIL+GAP | W8A8 dequant scale 崩溃 | 跨请求 identical 乱码 | 期望 `logits_finite`→未检出；乱码检测漏检 | 2624 / 1 / 0 |
| S23 | [cases/S23/](./cases/S23/) | PASS | 一层 `o_proj` 权重置零 | identical-mode 塌缩 | `token_repeat` | 2 / 17 / 48 |
| S45 | [cases/S45/](./cases/S45/) | FAIL+GAP | top-k 打在 −logits | 各不相同乱码 | 期望 `token_repeat`+`logits_finite`→未检出；乱码+重复检测都漏 | 16 / 0 / 0 |
| S43 | [cases/S43/](./cases/S43/) | PASS | embedding ×100 | 换行塌缩 | `token_repeat` | 16 / 40 / 48 |
| S22 | [cases/S22/](./cases/S22/) | PASS | Spec resample 无独立 salt | acceptance_rate 塌缩 | `spec_acceptance`（主） | 130 / 45 / 48 |
| S06 | [cases/S06/](./cases/S06/) | PASS | MoE router bias / mask | 进错专家、复读文本 | `token_repeat` | 70 / 1 / 1† |
| S26 | [cases/S26/](./cases/S26/) | PASS | RMSNorm fp32 错乘 | `1.1.1…` 复读 | `token_repeat` | 470 / 14 / 48 |
| S25 | [cases/S25/](./cases/S25/) | PASS | RoPE 后半维丢失 | `1.1.1…` / `1.0.0…` 复读 | `token_repeat` | 462 / 15 / 48 |
| S50 | [cases/S50/](./cases/S50/) | PASS | SwiGLU gate/up 对调 | identical `!!!!` | `logits_finite` | 58 / 48 / 48 |
| S48 | [cases/S48/](./cases/S48/) | PASS | residual 极性取反 | identical `!!!!` | `logits_finite` | 100 / 48 / 48 |
| S47 | [cases/S47/](./cases/S47/) | PASS | Attn 前 K/V 对调 | CJK / Trail 塌缩 | `token_repeat` | 58 / 37 / 48 |
| S33 | [cases/S33/](./cases/S33/) | PASS | softcap 缺 `*cap` rescale | `1.1.1…` 复读 | `token_repeat` | 132 / 15 / 48 |

计数摘自各包 `evidence/layers.json`（或归档已公布数）。脚注：

- **S06 †**：`layers.json` / status 写 `detect_reports=0`，但同次归档有 `token_repeat` report×1；表内 detect 按 report 记 **1**。
- **S07**：precision 记成 1，实为 identical×48 乱码（以 samples + score 为准）。
- **S45**：`precision=0` 是 identical-mode 低估；样本仍是各不相同乱码。
- **S01**：precision=25 含 CJK 误计可疑，详见包内说明。

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
