# S47 · 注意力前 K/V 对调（KV 不一致→定界）

公开案例包。注意力计算前把 K/V 对调。输出乱码/复读；重复检测抓住；KV 从 prompt 第 1 个 token、第 0 层起就和干净对照对不上。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 不一致→定界** |
| 检测 | **检出** |
| 三层率 | **30 / 0 / 48**（触发 / 计数器判坏=0 / 报告 48；另有 **37** 条内容相同的垃圾，以 samples 为准） |
| Detector | `token_repeat` |
| Origin | 见规格 |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) |
| 模型 | Qwen3-8B · TP2 · CARD=4,5 |
| Run | `keep-set-retest-20261022` · `S47-layers-20261023T111450` / `S47-pr19285-20261023T111625` |

## 1 · 现象

乱码或重复字串。自动「判坏」计数可能是 0，但 samples 里仍有多条**内容相同**的垃圾（本包记 37 条）——以 samples 为准。见 [evidence/samples/](./evidence/samples/)。

## 2 · 案例背景 / 构造

Attn 前 K/V 对调。细节见 [evidence/规格说明.md](./evidence/规格说明.md)。

## 3 · Guard 结果

**检出。** 触发 30；重复检测报告 48。结案：**KV 不一致→定界**——无数值崩溃；相似度从第 0 层起就不一致（见事实）。

## 4 · 复现技巧

| 项 | 怎么做 |
|----|--------|
| Overlay | 见规格 / 生成脚本 |
| detector | `token_repeat` |
| 对照 | 干净树上按 token id 原样重放 |

## 5 · 定界分析

### 事实

- **清洁标杆（≥2 组）：** 干净服务重放对照；**2 组**；shape 一致。对比窗约 `n_prompt=14`，prompt 长度 + 输出长度 − 1≈19。
- **两对同向：** 数值问题格 **0**；余弦从 prompt 第 1 个 token、**`model.layers.0`** 起就崩（余弦≈0.008）；同 token 最差约 −0.15 落在 `model.layers.8`。
- **dump 双名：** 全名排序下首次余弦也可能写在 `layer_36`（= `model.layers.0`），与上表模型层叙事一致。
- **未用槽：** 异常侧有限非 0（**卫生**）；标杆未用全 0。
- **三层旁注：** precision 计数可能为 0，但 samples 里仍有多条内容相同的垃圾（本包记 identical×37）——以 samples 为准。
- 证据：`evidence/kv_*.json`；`verified_kv/S47/`（**.pt 未入库**）。



### KV 对账表

分桶（可读性）：`≈1`≥0.99；`0.9–0.99`；`0.8–0.9`；`0.6–0.8`；`0.3–0.6`；`0.1–0.3`；`<0.1`（含负值）；数值问题写清子类型（如 `数值问题:全零(zero_norm)` / `数值问题:NaN` / `数值问题:Inf`），勿只写「数值异常」（不编余弦）。

数据来自 `evidence/kv_v516_numeric_first.json`（及同结构字段）；不编造未入库 `.pt` 上的数。

两对同向时只展示**代表对**（对 1）。

**代表对**（`req_id`=`cmpl-87d4b9f0f1e24e83-0-91bc86cf`；对比窗 **19** token，其中 prompt **14**）。

**表1 · 每 token 最差格**（该 token 上差距最大的层；有数值问题则整格写清子类型）

| token 序号 | 角色 | 该 token 最差格 |
| --- | --- | --- |
| 0 | prompt[0] | <0.1（最差 layer_41） |
| 1 | prompt[1] | <0.1（最差 L17） |
| 2 | prompt[2] | <0.1（最差 layer_65） |
| 3 | prompt[3] | <0.1（最差 L17） |
| 4 | prompt[4] | <0.1（最差 layer_45） |
| 5 | prompt[5] | <0.1（最差 L17） |
| 6 | prompt[6] | <0.1（最差 L19） |
| 7 | prompt[7] | <0.1（最差 L26） |
| 8 | prompt[8] | <0.1（最差 layer_47） |
| 9 | prompt[9] | <0.1（最差 L11） |
| 10 | prompt[10] | <0.1（最差 L19） |
| 11 | prompt[11] | <0.1（最差 layer_62） |
| 12 | prompt[12] | <0.1（最差 layer_44） |
| 13 | prompt[13] | <0.1（最差 L25） |
| 14 | out[0] | <0.1（最差 layer_36） |
| 15 | out[1] | <0.1（最差 layer_44） |
| 16 | out[2] | <0.1（最差 layer_44） |
| 17 | out[3] | <0.1（最差 layer_44） |
| 18 | out[4] | <0.1（最差 layer_44） |

**表2 · 首个出问题的 token 的逐层剖面（合并区间）** — **首个出问题的 token = prompt[0]**（证据 `first_cos_mismatch.token_idx=0`）。

| 层区间（model.layers） | 余弦 / 状态 |
| --- | --- |
| L0–L11 | <0.1 |

注：逐层余弦抽样止于 L11（包内 `clean_model_tok0_cos` 最多 12 层）；模型共 36 层。该 token 全层最差锚点：L8 = -0.1466（<0.1）。

### 推断

- 从第 0 层起相似度崩 → **KV 不一致可定界**；不定界到「K/V 对调」源码行以外的唯一断言。

### 结论

- 结案档：**KV 不一致→定界**（两组同向）。

## 6 · 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 补丁 |
| `evidence/规格说明.md` | 规格 |
| `evidence/三层计数.json` / `跑批结果.json` | 三层 / 摘要 |
| `evidence/samples/` / `reports/` | 样本 / 报告 |
| `evidence/kv_*.json` | 对账 |

## 7 · 上游 PR 关系

见规格。
