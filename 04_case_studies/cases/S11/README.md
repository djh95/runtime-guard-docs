# S11 · MLA RoPE pad（KV 不一致→定界）

公开案例包。MLA（多头潜在注意力）里 RoPE（旋转位置编码）pad 错位一类构造；输出 token 复读被检出；KV 对账从 prompt 很早的位置就开始和干净对照对不上。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 不一致→定界** |
| 检测 | **检出** |
| 三层率 | **108 / 27 / 48**（触发 / 判坏 / 报告） |
| Detector | `token_repeat` |
| Origin | 见规格 |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) |
| 模型 | DeepSeek-V2-Lite（MLA）· TP2 · CARD=4,5 |
| Run | `keep-set-retest-20261022` · `S11-layers-20261023T125037` |

## 1 · 现象

约 27/48 判坏；重复-token 检测命中。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 案例背景 / 构造

MLA prefill RoPE pad 错位。细节见 [evidence/规格说明.md](./evidence/规格说明.md)。

## 3 · Guard 结果

**检出。** **108 / 27 / 48**。结案：**KV 不一致→定界**——无数值崩溃；首个不一致在 prompt 第 2 个 token 一带（见事实）；两组同向。

## 4 · 复现技巧

| 项 | 怎么做 |
|----|--------|
| Overlay | `11_mla_rope_pad.patch` |
| 模型 | DeepSeek-V2-Lite |
| 负载 | 变长 prompt · 搅动 |
| detector | `token_repeat` |

## 5 · 定界分析

### 事实

- **清洁标杆（≥2 组）：** 干净服务重放对照；**2 组**；shape 一致（MLA 窗 `[1,128,1,64]`）。对比窗较长：约 `n_prompt=14`，生成较多，prompt 长度 + 输出长度 − 1≈39。
- **两对同向：** 无数值问题；都在 **prompt 第 2 个 token** 上出现余弦分歧。
- **余弦：** 首次明显不一致在 dump 名 `layer_27`（余弦≈0.96）；同 token 上最差约 0.24，落在 `model.layers.16`。prompt 第 1 个 token 的模型层仍接近 1.0。
- **dump 双名：** 与同系列 MLA 案相同——`layer_27` 是模型第 0 层的并行文件名（`layer_(27+i)` ↔ `model.layers.i`），不要读成「第 27 层根因」。
- 证据：`evidence/kv_*.json`（**.pt 未入库**）。



### KV 对账表

分桶（可读性）：`≈1`≥0.99；`0.9–0.99`；`0.8–0.9`；`0.6–0.8`；`0.3–0.6`；`0.1–0.3`；`<0.1`（含负值）；数值门闩写清子类型（如 `数值问题:全零(zero_norm)` / `数值问题:NaN` / `数值问题:Inf`），勿只写「数值异常」（不编余弦）。

数据来自 `evidence/kv_v516_numeric_first.json`（及同结构字段）；不编造未入库 `.pt` 上的数。

两对同向时只展示**代表对**（对 1）。

**代表对**（`req_id`=`cmpl-8a3c5f808dc7f05c-0-b6f2aeb5`；对比窗 **39** token，其中 prompt **14**）。

**表1 · 每 token 最差格**（该 token 上差距最大的层；有数值门闩则整格写清子类型）

| token 序号 | 角色 | 该 token 最差格 |
| --- | --- | --- |
| 0 | prompt[0] | ≈1（最差 layer_53） |
| 1 | prompt[1] | 0.1–0.3（最差 L16） |
| 2 | prompt[2] | 0.1–0.3（最差 L18） |
| 3 | prompt[3] | 0.1–0.3（最差 L12） |
| 4 | prompt[4] | 0.1–0.3（最差 L18） |
| 5 | prompt[5] | 0.1–0.3（最差 L20） |
| 6 | prompt[6] | 0.1–0.3（最差 L20） |
| 7 | prompt[7] | 0.3–0.6（最差 L12） |
| 8 | prompt[8] | 0.1–0.3（最差 L12） |
| 9 | prompt[9] | 0.1–0.3（最差 L12） |
| 10 | prompt[10] | 0.3–0.6（最差 L20） |
| 11 | prompt[11] | 0.1–0.3（最差 L14） |
| 12 | prompt[12] | 0.1–0.3（最差 L12） |
| 13 | prompt[13] | 0.3–0.6（最差 L12） |
| 14 | out[0] | 0.8–0.9（最差 layer_52） |
| 15 | out[1] | 0.3–0.6（最差 layer_28） |
| 16 | out[2] | 0.6–0.8（最差 L20） |
| 17 | out[3] | 0.8–0.9（最差 L14） |
| 18 | out[4] | 0.6–0.8（最差 layer_28） |
| 19 | out[5] | 0.8–0.9（最差 layer_28） |
| 20 | out[6] | 0.8–0.9（最差 L18） |
| 21 | out[7] | 0.8–0.9（最差 layer_28） |
| 22 | out[8] | 0.8–0.9（最差 layer_44） |
| 23 | out[9] | 0.9–0.99（最差 layer_44） |
| 24 | out[10] | 0.9–0.99（最差 L18） |
| 25 | out[11] | 0.9–0.99（最差 layer_44） |
| 26 | out[12] | 0.8–0.9（最差 layer_44） |
| 27 | out[13] | 0.9–0.99（最差 layer_28） |
| 28 | out[14] | 0.8–0.9（最差 layer_44） |
| 29 | out[15] | 0.9–0.99（最差 layer_44） |
| 30 | out[16] | 0.9–0.99（最差 layer_44） |
| 31 | out[17] | 0.8–0.9（最差 layer_28） |
| 32 | out[18] | 0.9–0.99（最差 layer_32） |
| 33 | out[19] | 0.8–0.9（最差 layer_44） |
| 34 | out[20] | 0.6–0.8（最差 L16） |
| 35 | out[21] | 0.9–0.99（最差 layer_28） |
| 36 | out[22] | 0.9–0.99（最差 L22） |
| 37 | out[23] | 0.8–0.9（最差 layer_28） |
| 38 | out[24] | 0.8–0.9（最差 layer_28） |

**表2 · 首个出问题的 token 的逐层剖面（合并区间）** — **首个出问题的 token = prompt[1]**（证据 `first_cos_mismatch.token_idx=1`；prompt[0] 仍 ≈1，画它没用）。

包内**没有** prompt[1] 的完整逐层余弦数组（仅有 `clean_model_tok0_cos` 给干净的 token0）→ **不画合并区间假表**。证据锚点：

| 锚点 | 值 |
| --- | --- |
| 角色 | prompt[1]（window token_idx=1） |
| 该 token 最差格 | 0.1–0.3（`min_cos`≈0.243 @ `model.layers.16`） |
| 同 token 另锚 | `layer_27` 上 cos≈0.960 |

注：完整逐层合并需服务器 `verified_kv/S11/` 重跑该 token 的 layerwise；禁止用 token0 的 ≈1 剖面冒充首坏。

### 推断

- 有效槽相似度已分 → 定界到本窗首分歧位置；**不定界到 RoPE 源码行**。

### 结论

- 结案档：**KV 不一致→定界**（两组同向）。

## 6 · 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 补丁 |
| `evidence/规格说明.md` | 规格 + 实测 |
| `evidence/三层计数.json` / `跑批结果.json` | 三层 / 摘要 |
| `evidence/samples/` / `reports/` | 样本 / 报告 |
| `evidence/kv_*.json` | 对账 |

## 7 · 上游 PR 关系

见规格（ascend#18798）。
