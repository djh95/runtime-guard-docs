# S33 · softcap 不完整（KV 一致→排除 KV）

公开案例包。logits softcap 少做了一步缩放（`*cap`）。输出出现数字/token 复读并被检出；KV 对账干净 → **排除 KV 主因**。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 一致→排除 KV** |
| 检测 | **检出** |
| 三层率 | **102 / 15 / 48**（触发 / 判坏 / 报告） |
| Detector | `token_repeat` |
| Origin | 见规格 |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) |
| 模型 | Qwen3-8B · TP2 · CARD=4,5 |
| Run | `keep-set-retest-20261022` · `S33-layers-20261023T112336` |

## 1 · 现象

部分数字 / token 复读（约 15/48）；重复检测命中。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 案例背景 / 构造

softcap 缺 `*cap` rescale。细节见 [evidence/规格说明.md](./evidence/规格说明.md)。**注意双树**：只改 Ascend、不改上游 vLLM 采样侧时，补丁可能 apply 失败。

## 3 · Guard 结果

**检出。** **102 / 15 / 48**。结案：**KV 一致→排除 KV**——有效槽无数值问题；相似度全程 ≥0.99（见事实）。

## 4 · 复现技巧

| 项 | 怎么做 |
|----|--------|
| Overlay | 见规格（常需动 Ascend + vLLM 两侧） |
| detector | `token_repeat` |
| 对照 | 干净树上按 token id 原样重放 |

## 5 · 定界分析

### 事实

- **清洁标杆（≥2 组）：** 干净服务重放对照；**2 组**；shape 一致。对比窗约 `n_prompt=14`，prompt 长度 + 输出长度 − 1≈20。
- **两对同向：** 数值问题格 **0**；余弦全程干净（prompt 第 1 个 token 最差仍≈1.0）。
- **未用槽：** 异常侧有限非 0（**卫生**）。
- **有效槽 / 未用槽：** 有效与未用须分写（见 skills v5.20.10）。本包 `kv_finite_unused.json`：异常侧未用可有有限非零残留；标杆未用可为全 0。**勿写「未用一定填 0」。**
- 证据：`evidence/kv_*.json`（**.pt 未入库**）。



### KV 对账表

分桶（可读性）：`≈1`≥0.99；`0.9–0.99`；`0.8–0.9`；`0.6–0.8`；`0.3–0.6`；`0.1–0.3`；`<0.1`（含负值）；数值问题写清子类型（如 `数值问题:全零(zero_norm)` / `数值问题:NaN` / `数值问题:Inf`），勿只写「数值异常」（不编余弦）。

数据来自 `evidence/kv_v516_numeric_first.json`（及同结构字段）；不编造未入库 `.pt` 上的数。

两对同向时只展示**代表对**（对 1）。

**代表对**（`req_id`=`cmpl-803db7636b89c584-0-88c429d9`；对比窗 **20** token，其中 prompt **14**）。

**表1 · 每 token 最差格**（该 token 上差距最大的层；有数值问题则整格写清子类型）

| token 序号 | 角色 | 该 token 最差格 |
| --- | --- | --- |
| 0 | prompt[0] | ≈1（最差 layer_67） |
| 1 | prompt[1] | ≈1（最差 layer_67） |
| 2 | prompt[2] | ≈1（最差 layer_61） |
| 3 | prompt[3] | ≈1（最差 layer_61） |
| 4 | prompt[4] | ≈1（最差 layer_69） |
| 5 | prompt[5] | ≈1（最差 layer_61） |
| 6 | prompt[6] | ≈1（最差 layer_71） |
| 7 | prompt[7] | ≈1（最差 layer_71） |
| 8 | prompt[8] | ≈1（最差 layer_71） |
| 9 | prompt[9] | ≈1（最差 layer_59） |
| 10 | prompt[10] | ≈1（最差 layer_47） |
| 11 | prompt[11] | ≈1（最差 layer_61） |
| 12 | prompt[12] | ≈1（最差 layer_63） |
| 13 | prompt[13] | ≈1（最差 layer_67） |
| 14 | out[0] | ≈1（最差 layer_63） |
| 15 | out[1] | ≈1（最差 layer_61） |
| 16 | out[2] | ≈1（最差 layer_71） |
| 17 | out[3] | ≈1（最差 layer_61） |
| 18 | out[4] | ≈1（最差 layer_63） |
| 19 | out[5] | ≈1（最差 layer_41） |

**表2 · 首个出问题的 token 的逐层剖面** — **无问题 token，跳过**（对比窗内每 token 最差余弦均 ≈1 / ≥0.99 → 排除 KV；不假装「首坏」）。

一行说明：代表对窗内全程 ≈1。

### 推断

- 对账匹配 → **排除 KV 主因**（本窗）。
- 复读更贴近 logits softcap 路径，而非已匹配的 KV 槽。

### 结论

- 结案档：**KV 一致→排除 KV**。

## 6 · 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 补丁 |
| `evidence/规格说明.md` | 规格 + 实测 |
| `evidence/三层计数.json` / `跑批结果.json` | 三层 / 摘要 |
| `evidence/samples/` / `reports/` | 样本 / 报告 |
| `evidence/kv_*.json` | 对账 |

## 7 · 上游 PR 关系

见规格。
