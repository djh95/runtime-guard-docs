# S61 · 单层计算平台（金标 B）

公开案例包。晚 decode token 起，表2 呈现「前 L−1 层≈1 → 第 L 层跌到≈0.9 → 其后平台 0.8–0.9」。专供定界金标 B 教学（层计算引入误差，而非 KV 中段污染）。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 不一致→定界** |
| 检测 | **检出** |
| 三层率 | **86 / 21 / 48**（触发 / 判坏 / 报告；48 请求） |
| Detector | `token_repeat` |
| Origin | 单层（及后续平台层）decode 门控 target-cos 写后污染（构造匹配） |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) |
| 模型 | Qwen3-8B · TP2 |
| Run | `keep-set-retest-20261022` · `S61-layers-20261024T235838` / dump `S61-pr19285-20261025T000103` |
| 金标 | **B 命中**（晚 first-bad + L12 跌 + 0.8–0.9 平台） |

## 1 · 现象

约 21/48 判坏；重复-token 检测命中。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 案例背景 / 构造

仅在晚 decode（`seq_lens ≥ 21`，对应约 token 20）对特定 name-layer 范围做写后 target-cos 混合。经验映射：污染 `model.layers.N` 的 cache 时，dump 名 `model.layers.(2N)` / `(2N+1)` 呈现该余弦——故 drop 用 name-layer 6（→ dump L12≈0.90），平台用 name-layer 7…17（→ dump L14…35≈0.85）。禁 NaN/fill。细节见 [evidence/规格说明.md](./evidence/规格说明.md)。

## 3 · Guard 结果

**检出。** **86 / 21 / 48**。结案：**KV 不一致→定界**——无数问题；晚 out first-bad；表2 早层≈1、L12≈0.9、其后平台 0.8–0.9。

## 4 · 复现技巧

| 项 | 怎么做 |
|----|--------|
| Overlay | `evidence/overlay.patch`（`61_gold_b_v11_range`） |
| 模型 | Qwen3-8B TP2 |
| detector | `token_repeat` |
| 对照 | 清洁树 force-feed |

## 5 · 定界分析

### 事实

- **清洁标杆（≥2 组）：** 同波 clean-ref；shape 一致。
- **两对同向：** 首坏均在 **token 20（out[5]）**；token 19 及更早全程≈1。
- **表2（tok20）：** L0–L11≈1；**L12≈0.90**；L13–L35 落在 **≈0.78–0.90** 平台（两对一致）。
- **无数问题：** 有效槽有限。
- 证据：`evidence/S61.full_tables.json`（**.pt** 在 builder 机耐久 `verified_kv/S61/`）。

### KV 对账表

**代表对**（`req_id`=`cmpl-95880f9e24aa407b-0-8515a6e1`；`n_prompt=15`）。

**表1 · 每 token 最差格（节选）**

| token 序号 | 角色 | 该 token 最差格 |
| --- | --- | --- |
| 0–19 | prompt…out[4] | ≈1 |
| 20 | out[5] | 进入层平台（见表面 2） |

**表2 · token 20 逐层剖面**

| 层 | cos（约） | 分桶 |
| --- | --- | --- |
| L0–L11 | ≈1.0 | ≈1 |
| L12 | ≈0.90 | 0.9–0.99 |
| L13–L35 | ≈0.80–0.90 | 0.8–0.9 |

### 推断

1. 首坏在较晚 decode token，且此前 token 全层≈1 → 非早期 KV 槽污染。
2. L12 起跌、其后维持 0.8–0.9 → 符合「第 L 层计算引入误差、后续层承接」教学形态。
3. 无数问题 → 定界走层剖面余弦，不走有限性门闩。

### 结论

**KV 不一致→定界**；教学点 = **金标 B**（晚 first-bad + 层平台）。本包为 origin-faithful 构造钉，不是某 PR 逐行反修。

## 6 · 证据

- `evidence/overlay.patch`
- `evidence/S61.full_tables.json` · `S61.kv_pairs_recap.json` · `S61.kv_finite_unused.json`
- `evidence/reports/` · `evidence/samples/`

## 7 · 上游 / 类比

无单一合并 PR 锚点；类比单层算子/注意力实现误差在层间传播。
