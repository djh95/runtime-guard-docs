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
- **两对同向：** 首坏均在 **token 20（out[5]）**；token 19 及更早全程≈1；其后 out[6]…out[24] 仍在对比窗内（`n_tokens=40`，非生成在 tok20 停住）。
- **有效槽 / 未用槽：** 有效槽无 NaN/Inf（有限数）。未用槽：异常侧 `any_unused_nonzero=true`（有限非零残留）；代表对标杆未用可为全 0（`S61.kv_finite_unused.json`）——**勿写「未用一定填 0」**。
- **表2（tok20=out[5]，代表对）：** L0–L11≈1；**L12≈0.87 起跌**；其后多数落在 0.6–0.9，**L13 / L33 有更深跌**（表1 最差格在 L33≈0.24）。第二对更贴近「L12≈0.9 + 0.8–0.9 平台」。
- **无数问题：** 有效槽无 NaN/Inf/全零。
- 证据：`evidence/S61.full_tables.json`（**.pt** 在 builder 机耐久 `verified_kv/S61/`）。

### KV 对账表

**代表对**（`req_id`=`cmpl-95880f9e24aa407b-0-8515a6e1`；`n_prompt=15`；对比窗 `n_tokens=40`＝`n_prompt+n_output−1` → **`n_output=26`**，角色 out[0]…out[24]；全窗见 `evidence/S61.full_tables.json`）。

分桶：`≈1`≥0.99；`0.9–0.99`；`0.8–0.9`；`0.6–0.8`；`0.3–0.6`；`0.1–0.3`；`<0.1`。

**表1 · 每 token 最差格**（代表对；首坏后 out 一并列出，不截断）

| token 序号 | 角色 | 该 token 最差格 |
| --- | --- | --- |
| 0–19 | prompt[0]…out[4] | ≈1 |
| 20 | out[5] | 0.1–0.3（min_cos≈0.24 @ L33；逐层见**表2**） |
| 21 | out[6] | 0.6–0.8（min_cos≈0.73 @ L33） |
| 22 | out[7] | 0.6–0.8（min_cos≈0.71 @ L29） |
| 23 | out[8] | 0.6–0.8（min_cos≈0.68 @ L35） |
| 24 | out[9] | 0.6–0.8（min_cos≈0.67 @ L33） |
| 25 | out[10] | 0.6–0.8（min_cos≈0.65 @ L23） |
| 26 | out[11] | 0.3–0.6（min_cos≈0.32 @ L27） |
| 27 | out[12] | 0.6–0.8（min_cos≈0.69 @ L13） |
| 28 | out[13] | 0.6–0.8（min_cos≈0.65 @ L23） |
| 29 | out[14] | 0.6–0.8（min_cos≈0.74 @ L35） |
| 30 | out[15] | 0.6–0.8（min_cos≈0.69 @ L17） |
| 31 | out[16] | 0.6–0.8（min_cos≈0.63 @ L33） |
| 32 | out[17] | 0.6–0.8（min_cos≈0.67 @ L35） |
| 33 | out[18] | 0.6–0.8（min_cos≈0.70 @ L13） |
| 34 | out[19] | 0.6–0.8（min_cos≈0.67 @ L35） |
| 35 | out[20] | <0.1（min_cos≈0.04 @ L33） |
| 36 | out[21] | 0.6–0.8（min_cos≈0.66 @ L23） |
| 37 | out[22] | 0.3–0.6（min_cos≈0.59 @ L35） |
| 38 | out[23] | 0.6–0.8（min_cos≈0.66 @ L33） |
| 39 | out[24] | 0.6–0.8（min_cos≈0.68 @ L35） |

**表2 · token 20（out[5]）逐层剖面**（代表对 `model.layers.*`；合并区间）

| 层 | cos（约） | 分桶 |
| --- | --- | --- |
| L0–L11 | ≈1.0 | ≈1 |
| L12 | ≈0.87 | 0.8–0.9 |
| L13 | ≈0.41 | 0.3–0.6 |
| L14–L32、L34–L35 | 多数 ≈0.76–0.96 | 多为 0.6–0.9 / 0.9–0.99 |
| L33 | ≈0.24 | 0.1–0.3（本 token 表1 最差格） |

（第二对 `cmpl-a27d63ee…` 同在 token 20 首坏；其 L12≈0.92、其后更贴近 0.8–0.9 平台，见同文件 pair1。）

### 推断

1. **表2「L12 起跌 / 层平台」锚定的 token = token 20（角色 out[5]）**——即本包 first-bad；该 token 上 L0–L11≈1、**L12 开始掉到≈0.87**（代表对；第二对 L12≈0.92）。不是 out[0]，也不是更早的 prompt。
2. 首坏前全程≈1 → 非早期 KV 槽污染；其后 out[6…] 仍低于≈1（表1 已列），说明坏点后 decode 继续写脏。
3. 代表对在 L13/L33 有更深跌（表1 最差 @ L33）；第二对更贴近「0.8–0.9 平台」教学简图——两对同向在「晚 first-bad + L12 起跌」。
4. 无数问题 → 定界走层剖面余弦，不靠「是否有限」单独定界。

### 结论

**KV 不一致→定界**；教学点 = **金标 B**（晚 first-bad + 层平台）。本包为 origin-faithful 构造钉，不是某 PR 逐行反修。

## 6 · 证据

- `evidence/overlay.patch`
- `evidence/S61.full_tables.json` · `S61.kv_pairs_recap.json` · `S61.kv_finite_unused.json`
- `evidence/reports/` · `evidence/samples/`

## 7 · 上游 / 类比

无单一合并 PR 锚点；类比单层算子/注意力实现误差在层间传播。
