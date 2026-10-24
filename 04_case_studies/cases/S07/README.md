# S07 · W8A8 量化 scale 崩溃（KV 不一致→定界 · 乱码漏检）

公开案例包。**异常必现**（48 次请求彼此相同的乱码），但专抓「非有限 logits」的检测 **0 份报告**——这是**乱码漏检**，**不是**「没出异常 / 没抓到 KV」。  
因为 detector 没响、走不了 on_trigger，所以对**已经乱码的异常请求**用 **`manual_dump`** 抓了异常侧 KV，再在干净树上抓**清洁标杆**对比；有效槽全零 → **KV 不一致→定界**。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 不一致→定界**（请求用到的 KV **全是 0**） |
| 检测 | **乱码漏检**（`logits_finite` → 0 报告；**≠ 无异常**） |
| 三层率 | **74 / 48 / 0**（触发 / 判坏·identical×48 / 报告=0） |
| Detector | 期望 `logits_finite` → **未命中**（仍有异常 KV） |
| Origin | 见规格 |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) |
| 模型 | Qwen3-8B-W8A8 · TP2 · CARD=4,5 · `192.168.13.160` / `rg-test-160` |
| 观测跑 | `S07-layers-20261023T123413`（三层 **74/48/0**） |
| 异常 KV 跑 | `S07-pr19285-20261023T124136`（**`manual_dump`** ×2） |
| 标杆跑 | `S07-ref-recap-20261023T124403` |

## 1 · 现象

本轮 **48** 次请求：**必现**跨请求内容相同的乱码（precision identical×48；见 [evidence/samples/](./evidence/samples/)）。  
**detect=0**：没有 `logits_finite` / `token_repeat` 报告文件——只说明**漏检**，**不**表示「没有异常、也没有异常 KV」。

## 2 · 案例背景 / 构造

W8A8 反量化 / scale 崩溃族。细节见 [evidence/规格说明.md](./evidence/规格说明.md)。

## 3 · Guard 结果

| 步骤 | 发生了什么 |
|------|------------|
| 观测 | `S07-layers-20261023T123413`：三层 **74 / 48 / 0**；武装 `logits_finite`，`detect_by` 空 |
| 异常 KV 从哪来 | **不是** on_trigger。另开 **`S07-pr19285-20261023T124136`**，对异常请求做 **`manual_dump`**（`incident_type=manual_trigger`；水位 wave **2** 与 **50**）；包内报告在 `evidence/reports/`（路径类 `report/manual_trigger/`） |
| 清洁标杆 | **`S07-ref-recap-20261023T124403`**：同一段 history force-feed 到未打 overlay 的干净服务；成对 **2** 组 |
| 服务器 .pt | `verified_kv/S07/`（**.pt 未入库**；摘要在 `evidence/kv_*.json`） |
| 定界 | 异常侧有效槽 **数值问题:全零(zero_norm)**（自 prompt[0]、L0 起）→ **KV 不一致→定界**；无余弦格（门闩挡住，不是「没抓到」） |

## 4 · 复现技巧

| 项 | 怎么做 |
|----|--------|
| Overlay | `07_quant_scale_collapse.patch` |
| 模型 | Qwen3-8B-W8A8 |
| detector | `logits_finite`（本窗预期打不中） |
| 抓 dump | **`manual_dump`**（非 on_trigger）水位递增；合入 #19285；本包 2 份 `report/manual_trigger` |

## 5 · 定界分析

### 事实

- **KV 从哪来（一眼看懂）：** 乱码**必现**且 detect=0 → 用 **`manual_dump`** 抓异常侧，不是「没抓到异常 KV」。异常 dump 跑 **`S07-pr19285-20261023T124136`**（代表 `req_id`：`cmpl-8e065448…` @ wave **2**、`cmpl-b08a72fe…` @ wave **50**；报告类 `manual_trigger`）。清洁标杆跑 **`S07-ref-recap-20261023T124403`**（未打 overlay）。成对 **2** 组；shape 一致（`[1,128,4,128]`）。**.pt** 在服务器 `verified_kv/S07/`，包内只留 `evidence/kv_*.json` 与 `evidence/reports/`。
- **清洁标杆：** 同一段 history 在干净服务上重放得到的对照 KV。抓 dump 时生成很短：报告 **输出只有 1 个 token**（`output_token_count=1`），可比长度主要是 prompt（本窗 `n_prompt=14`，history 按「prompt 长度 + 输出长度 − 1」 也是 14）。
- **两对同向：** 两对异常↔标杆的数值结论相同。
- **有效槽 / 「格」：** 有效槽 = 本请求真正用到的 KV 位置；「格」= 某一个 token × 某一层。本窗从 prompt 第 1 个 token 起，异常侧有效槽就是数值问题。
- **数值门闩（定界依据）：** 有效槽有限但 **整段范数 = 0**（**全是 0**）→ `数值问题:全零(zero_norm)`；优先用它定界，不再算余弦。
- **为何不算余弦：** 有效槽已全零，**余弦格数 = 0**——不是「没抓到 / 漏算」，是门闩挡住了。
- **dump 双名：** 同目录并存 `model.layers.0…35` 与 `layer_36…71`（`layer_(36+i)`↔`model.layers.i`）。全名排序先碰到 `layer_36`；同一事实在 **`model.layers.0`**。两对皆 prompt token0 起即 `zero_norm`。
- 证据：`evidence/kv_compare.json`、`kv_v516_numeric_first.json`、`kv_finite_unused.json`、`evidence/reports/`。



### KV 对账表

分桶（可读性）：`≈1`≥0.99；`0.9–0.99`；`0.8–0.9`；`0.6–0.8`；`0.3–0.6`；`0.1–0.3`；`<0.1`（含负值）；数值门闩写清子类型（如 `数值问题:全零(zero_norm)` / `数值问题:NaN` / `数值问题:Inf`），勿只写「数值异常」（不编余弦）。

数据来自 `evidence/kv_v516_numeric_first.json`。两对同向；展示代表对。

**代表对**（`req_id`=`cmpl-8e065448ae678178-0-9dfa8816`；对比窗 **14** token，其中 prompt **14**）。

**表1 · 每 token 最差格**（该 token 上差距最大的层；有数值门闩则整格写清子类型）

| token 序号 | 角色 | 该 token 最差格 |
| --- | --- | --- |
| 0 | prompt[0] | 数值问题:全零(zero_norm) |
| 1 | prompt[1] | 数值问题:全零(zero_norm) |
| 2 | prompt[2] | 数值问题:全零(zero_norm) |
| 3 | prompt[3] | 数值问题:全零(zero_norm) |
| 4 | prompt[4] | 数值问题:全零(zero_norm) |
| 5 | prompt[5] | 数值问题:全零(zero_norm) |
| 6 | prompt[6] | 数值问题:全零(zero_norm) |
| 7 | prompt[7] | 数值问题:全零(zero_norm) |
| 8 | prompt[8] | 数值问题:全零(zero_norm) |
| 9 | prompt[9] | 数值问题:全零(zero_norm) |
| 10 | prompt[10] | 数值问题:全零(zero_norm) |
| 11 | prompt[11] | 数值问题:全零(zero_norm) |
| 12 | prompt[12] | 数值问题:全零(zero_norm) |
| 13 | prompt[13] | 数值问题:全零(zero_norm) |

**表2 · 首个出问题的 token 的逐层剖面（合并区间）** — **首个出问题的 token = prompt[0]**（证据 `first_numeric_issue` @ token_idx=0；`数值问题:全零(zero_norm)`）。

| 层区间（model.layers） | 余弦 / 状态 |
| --- | --- |
| L0–L35 | 数值问题:全零(zero_norm) |

注：证据 `数值问题:zero_norm`（有限但全零）；自 prompt[0]、`model.layers.0` / `layer_36` 起覆盖对比窗全部有效格；无余弦格。

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
