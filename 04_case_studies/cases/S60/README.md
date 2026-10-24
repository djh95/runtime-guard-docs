# S60 · PD 类中段槽污染（金标 A · 坏→恢复）

公开案例包。Prefill 写完后在首 decode 步污染 **prompt 中段槽**；KV 对账出现「中段坏 → 后续 prompt 又≈1 → out 再偏」链，专供定界金标 A 教学（污染/交接时序）。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 不一致→定界** |
| 检测 | **检出** |
| 三层率 | **3456 / 18 / 38**（触发 / 判坏 / 报告；48 请求；trigger 为各层首 decode 打点累计） |
| Detector | `token_repeat` |
| Origin | PD 类 post-prefill 单槽污染（构造匹配；非真 Mooncake 1P1D） |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) |
| 模型 | Qwen3-8B · TP2 |
| Run | `keep-set-retest-20261022` · `S60-layers-20261024T223939` |
| 金标 | **A 核心命中（坏→恢复）**；out[0] 早层≈0.8 **未齐**（见事实） |

## 1 · 现象

约 18/48 判坏；重复-token 检测命中。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 案例背景 / 构造

首 decode 时对已写完的 prompt 中段槽（默认 token 5）做 K/V 符号取反——模拟「算对了、之后 cache 被污染」。无 overlay 的清洁对照不注入。细节见 [evidence/规格说明.md](./evidence/规格说明.md)。

## 3 · Guard 结果

**检出。** **3456 / 18 / 38**。结案：**KV 不一致→定界**——无数问题；表1 可见中段坏后多个 prompt 恢复≈1。

## 4 · 复现技巧

| 项 | 怎么做 |
|----|--------|
| Overlay | `evidence/overlay.patch` / `gen_s60_overlay.py` |
| 模型 | Qwen3-8B TP2 |
| detector | `token_repeat` |
| 对照 | 清洁树 force-feed 报告 token id |

## 5 · 定界分析

### 事实

- **清洁标杆（≥2 组）：** 同波 clean-ref；shape 一致（`[1,128,4,128]`）。
- **两对同向：** 均无数值门闩；首坏均在 **prompt[5]**（cos≈−1）；prompt[6…] 最差格回到≈1。
- **out[0]：** 最差格约 0.96（偏晚层）；**早层（L0–8）仍≈1**——未达到金标「out0 从第 1 层起≈0.8」。结构原因：槽污染改变的是对 mid 的 attention 读，out[0] 自身 L0 的 K/V 投影仍可接近标杆。
- **仅 PD：** 本钉点 = overlay 武装的 PD **类**时序；清洁无 overlay 为对照。真 1P1D 未在本包拓扑验证。
- 证据：`evidence/S60.full_tables.json`（**.pt** 在 builder 机耐久 `verified_kv/S60/`）。

### KV 对账表

分桶：`≈1`≥0.99；`0.9–0.99`；`0.8–0.9`；…；`<0.1`。

**代表对**（`req_id`=`cmpl-80ce8d173f53bf87-0-b1c8cd6c`；对比窗含 prompt **15**）。

**表1 · 每 token 最差格**（节选至 out 前段；全窗见 `S60.full_tables.json`）

| token 序号 | 角色 | 该 token 最差格 |
| --- | --- | --- |
| 0–4 | prompt[0–4] | ≈1 |
| 5 | prompt[5] | <0.1（最差 L0，cos≈−1） |
| 6–14 | prompt[6–14] | ≈1（恢复） |
| 15 | out[0] | 0.9–0.99（最差约 L33，cos≈0.96） |

**表2 · 首坏 token（prompt[5]）逐层剖面（前段）**

| 层 | 分桶 | cos |
| --- | --- | --- |
| L0–L15 | <0.1 | ≈−1.0 |

（该 token 全层近满污染；与「只脏中段槽」一致。out[0] 逐层见 evidence 全表——早层≈1，晚层略降。）

### 推断

1. prompt[5] 在写 cache 时算对（否则不会出现「其后 prompt 又≈1」）→ **之后**该槽被污染。
2. out[0] 有二次偏离但形态弱于金标早层≈0.8 → 可继续追 PD 真拓扑 / 污染强度，**不能**单凭本包写死「传输根因=某 PR」。
3. 无数问题 → 定界走余弦时序，不走有限性门闩。

### 结论

**KV 不一致→定界**；教学点 = **坏→恢复** 污染时序（金标 A 核心）。out0 早层≈0.8 与真 PD 复现仍为已知缺口，已写进事实，不拔高。

## 6 · 证据

- `evidence/overlay.patch`
- `evidence/S60.full_tables.json` · `S60.kv_pairs_recap.json` · `S60.kv_finite_unused.json`
- `evidence/reports/` · `evidence/samples/`

## 7 · 上游 / 类比

无单一合并 PR 锚点；故障类比 PD reformat / KV 交接写歪（如 early-reformat 类史）。本包为 **origin-faithful 时序构造**，不是某 PR 的逐行反修。
