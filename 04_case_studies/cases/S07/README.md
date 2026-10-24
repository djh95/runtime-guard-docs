# S07 · W8A8 量化 scale 崩溃（KV 不一致→定界 · 乱码漏检）

公开案例包。**乱码肉眼可见，但 logits（模型算分）仍有限**，专抓「非有限 logits」的检测没响——**乱码漏检**。认乱码看 samples；异常 KV 靠事后**手动触发 dump**（不是检测一响就自动抓）。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 不一致→定界**（请求用到的 KV **全是 0**） |
| 检测 | **乱码漏检**（期望 `logits_finite` → 0 份报告） |
| 三层率 | **74 / 48 / 0**（触发 / 判坏 / 报告；48 次相同乱码，但报告数=0） |
| Detector | 期望 `logits_finite` → **未命中** |
| Origin | 见规格 |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) |
| 模型 | Qwen3-8B-W8A8 · TP2 · CARD=4,5 · `192.168.13.160` / `rg-test-160` |
| Run | `keep-set-retest-20261022` · `S07-layers-20261023T123413` |

## 1 · 现象

48 次请求得到**彼此相同**的乱码（见 [evidence/samples/](./evidence/samples/)）。**没有**检测报告文件。

## 2 · 案例背景 / 构造

W8A8 反量化 / scale 崩溃族。细节见 [evidence/规格说明.md](./evidence/规格说明.md)。

## 3 · Guard 结果

**乱码漏检。** **74 / 48 / 0**（武装的是 `logits_finite`，`detect_by` 空；**没有** `token_repeat` 报告）。异常 KV **不是** on_trigger：layers 跑完见 48 条 identical 乱码且 0 报告后，另开 `S07-pr19285-…` 用 **`manual_dump`（`incident_type=manual_trigger`）** 水位递增抓了 **2** 个请求（wave 2 / wave 50），再 force-feed 干净树做对照。结案：**KV 不一致→定界**——有效槽从 prompt 开头、模型第 0 层起就是全零；没有可算的相似度格（见事实）。

## 4 · 复现技巧

| 项 | 怎么做 |
|----|--------|
| Overlay | `07_quant_scale_collapse.patch` |
| 模型 | Qwen3-8B-W8A8 |
| detector | `logits_finite`（本窗预期打不中） |
| 抓 dump | 手动 dump 水位递增 + #19285 |

## 5 · 定界分析

### 事实

- **清洁标杆（≥2 组）：** 用同一段 history，在**未打 overlay 的干净服务**上重放，抓到的 KV 当作对照。本包成对 **2 组**；两边张量 shape 一致（`[1,128,4,128]`）。抓 dump 时生成很短：报告里 `output_token_count=1`（常写作 **`o=1`**），可比长度主要是 prompt（本窗 `n_prompt=14`，history 按 `p+o−1` 也是 14 个 token）。
- **两对同向：** 下面说的数值结论在 **两对异常↔标杆** 上相同，不是一对有、一对没有。
- **有效槽 / 「格」：** 有效槽 = 当前请求真正用到的 KV 位置；对账时「某一个 token × 某一层」算一格。本窗从 prompt 第 1 个 token 起，异常侧有效槽就被判成数值问题。
- **数值门闩（`zero_norm`）：** 有限性检查发现：这些有效槽里的数都是有限的（不是 NaN/Inf），但 **整段范数 = 0**，也就是 **全是 0**。脚本把这种「有限但全零」标成 `数值问题:zero_norm`，并优先用它定界，而不是再去算和标杆有多像。
- **为何不算余弦：** 余弦比较要两边都是「可比较的正常数值」。有效槽已经全零（数值问题），本窗统计里 **余弦格数 = 0**，所以 **没有**「第一处余弦分叉在哪一层」可写——不是漏算，是门闩挡住了。
- **dump 双名（为何 `layer_36` = `model.layers.0`，不是第 36 层）：** 同一次 dump 目录里并存两套文件名，各 36 个（合计 72）。一套叫 `model.layers.0…35.self_attn.attn`（模型层号）；另一套叫 `layer_36…71`。按编号一一对应：`layer_(36+i)` ↔ `model.layers.i`（例如 `layer_36`↔`model.layers.0`，`layer_37`↔`model.layers.1`）。对账脚本按名字排序时，会先碰到 `layer_36`，所以「全名首次数值问题」写在 `layer_36`；若只看 `model.layers.*`，同一事实落在 **`model.layers.0`**。两对都是：prompt token0 起即 `zero_norm`。
- 证据：`evidence/kv_compare.json`、`kv_v516_numeric_first.json`、`kv_finite_unused.json`（**.pt 未入库**；服务器 `verified_kv/S07/`）。



### KV 对账表

分桶（可读性）：`≈1`≥0.99；`0.9–0.99`；`0.8–0.9`；`0.6–0.8`；`0.3–0.6`；`0.1–0.3`；`<0.1`（含负值）；有 NaN/Inf/zero_norm 等数值门闩则写 **数值异常**（不编余弦）。

数据来自 `evidence/kv_v516_numeric_first.json`。两对同向；展示代表对。

**代表对**（`req_id`=`cmpl-8e065448ae678178-0-9dfa8816`；对比窗 **14** token，其中 prompt **14**）。

**表1 · 每 token 最差格**（该 token 上差距最大的层；有数值门闩则整格写数值异常）

| token 序号 | 角色 | 该 token 最差格 |
| --- | --- | --- |
| 0 | prompt[0] | 数值异常 |
| 1 | prompt[1] | 数值异常 |
| 2 | prompt[2] | 数值异常 |
| 3 | prompt[3] | 数值异常 |
| 4 | prompt[4] | 数值异常 |
| 5 | prompt[5] | 数值异常 |
| 6 | prompt[6] | 数值异常 |
| 7 | prompt[7] | 数值异常 |
| 8 | prompt[8] | 数值异常 |
| 9 | prompt[9] | 数值异常 |
| 10 | prompt[10] | 数值异常 |
| 11 | prompt[11] | 数值异常 |
| 12 | prompt[12] | 数值异常 |
| 13 | prompt[13] | 数值异常 |

**表2 · 首 token 逐层剖面（合并区间）** — 首 token = **prompt[0] / window token0**（与证据 `token_idx=0` 一致）。

| 层区间（model.layers） | 余弦 / 状态 |
| --- | --- |
| L0–L35 | 数值异常 |

注：状态为 zero_norm（有限但全零）；无余弦格。

### 推断

- 有效槽全零 → **定界到数值问题（全零）**；本窗不能用相似度指出「第一坏层」。
- 与「乱码漏检」并列：检测抓不住乱码，但对账仍能定界。

### 结论

- 结案档：**KV 不一致→定界**（数值门闩；两组同向）。
- 检测侧：**乱码漏检**。

## 6 · 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 补丁 |
| `evidence/规格说明.md` | 规格 + 实测 |
| `evidence/三层计数.json` / `跑批结果.json` | 三层 / 摘要 |
| `evidence/samples/` | 乱码样本 |
| `evidence/reports/` | 手动触发的报告 |
| `evidence/kv_*.json` | 对账 / 有限性 |

## 7 · 上游 PR 关系

见规格（#37442 族）。
