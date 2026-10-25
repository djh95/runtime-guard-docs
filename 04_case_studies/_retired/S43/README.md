# S43 · Embedding ×100（KV 不一致→定界）

公开案例包。把 embedding 放大 100 倍。输出几乎只剩换行/空白，且多条请求内容相同；重复检测抓住；KV 从 prompt 第 1 个 token 起就和干净对照对不上。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 不一致→定界** |
| 检测 | **检出** |
| 三层率 | **16 / 40 / 48**（触发 / 判坏 / 报告；`token_repeat`×48；**trigger≪precision 正常**：embed×100 每次生效，但 `ANOMALY_TRIGGER` 日志限频） |
| Detector | `token_repeat` |
| Origin | 见规格 |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) |
| 模型 | Qwen3-8B · TP2 · CARD=4,5 |
| Run | `keep-set-retest-20261022` · `S43-layers-20261023T104944` / `S43-pr19285-20261023T105118` / `S43-ref-recap-20261023T105259` |

## 1 · 现象

大量「输出几乎只剩换行」：输出几乎只剩换行/空白；约 40 条内容相同。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 案例背景 / 构造

embedding 权重 ×100。细节见 [evidence/规格说明.md](./evidence/规格说明.md)。

## 3 · Guard 结果

**检出。** **16 / 40 / 48**（40 条相同换行塌缩；trigger 只反映限频后的开火日志，**低于**判坏数不反常）。结案：**KV 不一致→定界**——无数值崩溃；从 prompt 第 1 个 token 起相似度就不一致（见事实）。

## 4 · 复现技巧

| 项 | 怎么做 |
|----|--------|
| Overlay | 见规格 / 生成脚本 |
| detector | `token_repeat` |
| 对照 | 干净树上按 token id 原样重放 |

## 5 · 定界分析

### 事实

- **清洁标杆（≥2 组）：** 干净服务重放对照；shape 一致；标杆未用槽归零。history 按「prompt 长度 + 输出长度 − 1」≈ **18**（约 prompt=14、生成较短）。
- **两对同向：** 无数值问题；余弦可算，且两对同一套层叙事。
- **余弦：** prompt 第 1 个 token 起，`model.layers.0–1` 仍≈1；自 **`model.layers.2`** 首次明显偏离（余弦≈0.55）；同 token 最差约 −0.30 落在 `model.layers.20`。
- **dump 双名：** 另有 `layer_36…` 一套名字；`layer_36` = `model.layers.0`（`layer_(36+i)` ↔ `model.layers.i`）。全名排序的「首次余弦」可能先写到 `layer_36`，与「模型第 2 层首越阈」是同一对账的不同命名视图。
- **未用槽：** 异常侧有限非 0（**卫生**）。
- 证据：`evidence/kv_*.json`；`verified_kv/S43/`（**.pt 未入库**）。



### KV 对账表

分桶（可读性）：`≈1`≥0.99；`0.9–0.99`；`0.8–0.9`；`0.6–0.8`；`0.3–0.6`；`0.1–0.3`；`<0.1`（含负值）；数值问题写清子类型（如 `数值问题:全零(zero_norm)` / `数值问题:NaN` / `数值问题:Inf`），勿只写「数值异常」（不编余弦）。

数据来自 `evidence/kv_v516_numeric_first.json`（及同结构字段）；不编造未入库 `.pt` 上的数。

两对同向时只展示**代表对**（对 1）。

**代表对**（`req_id`=`cmpl-895abf4495ac06e2-0-a66dbfba`；对比窗 **18** token，其中 prompt **14**）。

**表1 · 每 token 最差格**（该 token 上差距最大的层；有数值问题则整格写清子类型）

| token 序号 | 角色 | 该 token 最差格 |
| --- | --- | --- |
| 0 | prompt[0] | <0.1（最差 L20） |
| 1 | prompt[1] | <0.1（最差 layer_37） |
| 2 | prompt[2] | <0.1（最差 layer_37） |
| 3 | prompt[3] | <0.1（最差 L33） |
| 4 | prompt[4] | <0.1（最差 L13） |
| 5 | prompt[5] | <0.1（最差 L6） |
| 6 | prompt[6] | <0.1（最差 layer_43） |
| 7 | prompt[7] | <0.1（最差 layer_43） |
| 8 | prompt[8] | <0.1（最差 layer_43） |
| 9 | prompt[9] | <0.1（最差 L11） |
| 10 | prompt[10] | <0.1（最差 L6） |
| 11 | prompt[11] | <0.1（最差 L23） |
| 12 | prompt[12] | <0.1（最差 L15） |
| 13 | prompt[13] | <0.1（最差 L13） |
| 14 | out[0] | <0.1（最差 L23） |
| 15 | out[1] | <0.1（最差 L23） |
| 16 | out[2] | <0.1（最差 L21） |
| 17 | out[3] | <0.1（最差 L21） |

**表2 · 首个出问题的 token 的逐层剖面（合并区间）** — **首个出问题的 token = prompt[0]**（证据 `first_cos_mismatch.token_idx=0`）。

| 层区间（model.layers） | 余弦 / 状态 |
| --- | --- |
| L0–L1 | ≈1 |
| L2–L4 | 0.3–0.6 |
| L5 | 0.1–0.3 |
| L6 | 0.9–0.99 |
| L7 | 0.3–0.6 |
| L8 | 0.6–0.8 |
| L9–L10 | 0.3–0.6 |
| L11 | <0.1 |

注：逐层余弦抽样止于 L11（包内 `clean_model_tok0_cos` 最多 12 层）；模型共 36 层。该 token 全层最差锚点：L20 = -0.2952（<0.1）。

### 推断

- 相似度从很早的层就开始偏 → **KV 不一致可定界到本窗首分歧**；不定界到「embedding×100」源码行以外的断言。

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
