# S50 · SwiGLU gate/up 对调（KV 不一致→定界）

公开案例包。SwiGLU 的 gate/up 半边对调（反向注入）。输出全是 `!!!!…`；logits 非有限检测 48/48 命中；KV 对账：前面层相似度先裂开，稍后层出现 NaN——**KV 不一致→定界**（两组同向）。**构造算子名≠已证根因。**

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 不一致→定界** |
| 检测 | **检出** |
| 三层率 | **58 / 48 / 48**（触发 / 判坏 / 报告；全是 `logits_finite`） |
| Detector | `logits_finite` |
| Origin | `both` |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) |
| 模型 | Qwen3-8B · TP2 · CARD=4,5 |
| Run | 英文河名短句 ×48；`keep-set-retest-20261022` |

## 1 · 现象

全请求 `!!!!…`（48 条相同）；采样前 logits 非有限（报告里记为 nan）。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 案例背景 / 构造

反向注入：SwiGLU 先 `cat(up, gate)` 再走 `npu_swiglu`。细节见 [evidence/规格说明.md](./evidence/规格说明.md)。

## 3 · Guard 结果

**检出。** **58 / 48 / 48**。结案：**KV 不一致→定界**——先做数值门闩（有没有 NaN），再在仍有限的格子上看相似度；两组同向（见事实）。

钉点报告：prompt 长度 14；dump 时只生成 1 个 token。

## 4 · 复现技巧（必读）

| 项 | 怎么做 |
|----|--------|
| Overlay | `gen_s50_overlay.py` |
| Prompt | `Name one famous river. One short English sentence. id={i}.` |
| 并发 | **48** |
| 其它 | 温度 0；`max_tokens` 足以打出 `!!!!` |
| detector | `logits_finite`（可兼开复读检测） |
| 抓 dump | 非空 prompt token 列表 → 临时 #19285；抓前清 kv cache |
| 对照 | **干净树、无 overlay**；确认对照未亮 `logits_finite`；手动 dump + 按 token id 重放 |

## 5 · 定界分析

### 事实

- **现象与检测：** 全请求 `!!!!…`；`logits_finite` 48/48 命中（report 里 `finite_kind=nan`）。三层 **58 / 48 / 48**。
- **清洁标杆（≥2 组）：** 干净服务重放对照；标杆未亮 `logits_finite`；shape `[1,128,4,128]`。prompt=14，**`o=1`**，history `p+o−1=14`（从 prompt 第 1 个 token 起即可比）。
- **两对同向（数值门闩 + 干净格余弦）：**
  - **数值门闩：** 在 `model.layers.*` 上，prompt token0 起第 **6** 层开始出现异常侧 NaN（`buggy_nan`）；第 0–5 层仍有限。
  - **余弦（只在仍有限的「干净格」上算）：** 同 token 上首次低于 0.99 约在第 **3** 层（余弦≈0.989）；第 5 层最差可到约 −0.02；第 0–2 层仍≈1。
- **dump 双名：** 目录里两套各 36 个名字——`layer_36…71` 与 `model.layers.0…35…`。对应 `layer_(36+i)` ↔ `model.layers.i`，故 **`layer_36` = 模型第 0 层**，不是「第 36 层」。若按全名排序，`layer_*` 从 token0 起 used 槽全 NaN，会先报到 `layer_36`；层叙事以 `model.layers` 表为准。
- **未用槽：** 异常侧亦有 NaN（严重）；标杆未用槽全 0。
- 证据：`evidence/kv_compare.json`、`kv_v516_numeric_first.json`；`verified_kv/S50/`（**.pt 未入库**）。



### KV 对账表

分桶（可读性）：`≈1`≥0.99；`0.9–0.99`；`0.8–0.9`；`0.6–0.8`；`0.3–0.6`；`0.1–0.3`；`<0.1`（含负值）；数值门闩写清子类型（如 `数值问题:全零(zero_norm)` / `数值问题:NaN` / `数值问题:Inf`），勿只写「数值异常」（不编余弦）。

数据来自 `evidence/kv_v516_numeric_first.json` / `kv_compare.json`。两对同向；展示代表对。

**代表对**（`req_id`=`cmpl-80dfca0aa2091acb-0-ac611d71`；对比窗 **14** token，其中 prompt **14**）。

**表1 · 每 token 最差格**

| token 序号 | 角色 | 该 token 最差格 |
| --- | --- | --- |
| 0 | prompt[0] | 数值问题:NaN |
| 1 | prompt[1] | 数值问题:NaN |
| 2 | prompt[2] | 数值问题:NaN |
| 3 | prompt[3] | 数值问题:NaN |
| 4 | prompt[4] | 数值问题:NaN |
| 5 | prompt[5] | 数值问题:NaN |
| 6 | prompt[6] | 数值问题:NaN |
| 7 | prompt[7] | 数值问题:NaN |
| 8 | prompt[8] | 数值问题:NaN |
| 9 | prompt[9] | 数值问题:NaN |
| 10 | prompt[10] | 数值问题:NaN |
| 11 | prompt[11] | 数值问题:NaN |
| 12 | prompt[12] | 数值问题:NaN |
| 13 | prompt[13] | 数值问题:NaN |

**表2 · 首个出问题的 token 的逐层剖面（合并区间）** — **首个出问题的 token = prompt[0]**（证据 `first_numeric_issue` / 余弦门闩均自 token_idx=0；`数值问题:buggy_nan` 自 L6）。

| 层区间（model.layers） | 余弦 / 状态 |
| --- | --- |
| L0–L2 | ≈1 |
| L3 | 0.9–0.99 |
| L4 | 0.8–0.9 |
| L5 | <0.1 |
| L6–L35 | 数值问题:NaN |

注：证据 `数值问题:buggy_nan`：`model.layers` 上 L6–L35 自 token0 起 used 槽为 NaN；并行名 `layer_36…71` 自 token0 起亦全 NaN。表1 每 token 因含 NaN 格记为 NaN（L0–L5 仍有限可算余弦，见表2）。

### 推断

- prompt 第 1 个 token 起：相似度在第 3 层越阈、第 6 层起 NaN → **KV 不一致**且可写层事实。
- **不能**单凭此推出「根因=SwiGLU 对调」或「根因=KV 子系统」。
- 未开算子级 msprobe（殿后）。

### 结论

- 结案档：**KV 不一致→定界**（两组同向；含层事实）。
- 尚未证到构造根因算子名。

## 6 · 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 补丁 |
| `evidence/规格说明.md` | 规格 |
| `evidence/三层计数.json` / `跑批结果.json` | 三层 / 摘要 |
| `evidence/samples/` / `reports/` | 样本 / 报告 |
| `evidence/kv_*.json` | 对账 |

## 7 · 上游 PR 关系

| 链接 | 角色 |
|------|------|
| （构造反向注入；见规格） | 背景，非本包 KV 已证根因 |
| [ascend#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) | 抓 dump 辅助 |
