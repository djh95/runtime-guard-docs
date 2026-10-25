# S26 · RMSNorm fp32 错乘（KV 一致→排除 KV）

公开案例包。RMSNorm 权重在错误精度路径上相乘（反向注入）。输出 `1.1.1…` 复读被检出；KV 对账与干净对照对得上 → **排除 KV 主因**。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 一致→排除 KV** |
| 检测 | **检出** |
| 三层率 | **470 / 14 / 48**（触发可浮动；**报告 48/48**） |
| Detector | `token_repeat`（阈值=8） |
| Origin | 见规格 |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) |
| 模型 | Qwen3-8B · TP2 · CARD=4,5 |
| Run | 英文河名短句 × 48 并发 + 阈值 8；`keep-set-retest-20261022` |

## 1 · 现象

反复数字串；重复检测命中。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 案例背景 / 构造

RMSNorm fp32 错乘路径（反向注入）。细节见 [evidence/规格说明.md](./evidence/规格说明.md)。

## 3 · Guard 结果

**检出。** **470 / 14 / 48**。结案：**KV 一致→排除 KV**（对比窗内相似度几乎为 1；见事实）。

## 4 · 复现技巧（必读）

| 项 | 怎么做 |
|----|--------|
| Overlay | `gen_s26_overlay.py` |
| Prompt | 英文河名短句 ×48 并发 |
| detector | `token_repeat` 阈值 8 |
| 抓 dump | 非空 prompt token 列表 → 临时 #19285 |

## 5 · 定界分析

### 事实

- **有效槽 / 未用槽：** 有效与未用须分写（见 skills v5.20.10）。本包 `kv_finite_unused.json`：未用槽多数为 0，亦可有有限非零残留——**勿写「未用一定填 0」。**
- **现象与三层：** 输出常成 `1.1.1…` / `1.0.0…` 复读；三层 **470 / 14 / 48**（`token_repeat` 检出 48）。样本见 `evidence/samples/`。
- **清洁标杆（≥2 组）：** 干净服务重放对照。钉点 report 均非空 prompt（#19285）：一组约 prompt=14、output=8，另一组 prompt=14、output=17。
- **对比窗口：** **`n_tokens` = prompt 长度 + 输出长度 − 1**（两组分别为 21、30）。
- **两对同向：** 对比窗内各层余弦最低仍 ≥0.999988；**没有**首个不一致；无全 NaN 崩溃。
- 服务器 dump：`verified_kv/S26/`（**.pt 未入库**）；包内摘要 `kv_compare.json`。



### KV 对账表

分桶（可读性）：`≈1`≥0.99；`0.9–0.99`；`0.8–0.9`；`0.6–0.8`；`0.3–0.6`；`0.1–0.3`；`<0.1`（含负值）；数值问题写清子类型（如 `数值问题:全零(zero_norm)` / `数值问题:NaN` / `数值问题:Inf`），勿只写「数值异常」（不编余弦）。

数据来自 `evidence/kv_compare.json` 代表对（`req_id`=`cmpl-9dc6d291ed4ee37d-0-a45e21f3`；窗 30 token / prompt 14）。两对均为 match。

**表1 · 每 token 最差格**（证据只有每 token 的 `min_cos`，**无最差层名**）

| token 序号 | 角色 | 该 token 最差格 |
| --- | --- | --- |
| 0 | prompt[0] | ≈1 |
| 1 | prompt[1] | ≈1 |
| 2 | prompt[2] | ≈1 |
| 3 | prompt[3] | ≈1 |
| 4 | prompt[4] | ≈1 |
| 5 | prompt[5] | ≈1 |
| 6 | prompt[6] | ≈1 |
| 7 | prompt[7] | ≈1 |
| 8 | prompt[8] | ≈1 |
| 9 | prompt[9] | ≈1 |
| 10 | prompt[10] | ≈1 |
| 11 | prompt[11] | ≈1 |
| 12 | prompt[12] | ≈1 |
| 13 | prompt[13] | ≈1 |
| 14 | out[0] | ≈1 |
| 15 | out[1] | ≈1 |
| 16 | out[2] | ≈1 |
| 17 | out[3] | ≈1 |
| 18 | out[4] | ≈1 |
| 19 | out[5] | ≈1 |
| 20 | out[6] | ≈1 |
| 21 | out[7] | ≈1 |
| 22 | out[8] | ≈1 |
| 23 | out[9] | ≈1 |

注：`per_token_head` 只归档了前 24 / 30 个 token；其余不编造。

**表2 · 首个出问题的 token 的逐层剖面** — **无问题 token，跳过**（对比窗全程 ≈1 → 排除 KV）。本包亦无逐层余弦数组，不画假表。

### 推断

- 对账匹配 → **排除 KV 主因**（本窗）。
- 复读仍在 → 更可能在 Norm/精度路径，而非本窗已匹配的 KV 槽。

### 结论

- 结案档：**KV 一致→排除 KV**。

## 6 · 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 补丁 |
| `evidence/规格说明.md` | 规格 |
| `evidence/三层计数.json` / `跑批结果.json` | 三层 / 摘要 |
| `evidence/samples/` / `reports/` | 样本 / 报告 |
| `evidence/kv_compare.json` | 对账摘要 |

## 7 · 上游 PR 关系

见规格。
