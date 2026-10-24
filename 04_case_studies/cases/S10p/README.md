# S10′ · FullAttn 回收块未清零（KV 一致→排除 KV）

公开案例包。目录名 `S10p` = S10′。构造预期像「回收的注意力 KV 块没擦干净」，**本窗对账却干净** → 结案 **排除 KV 主因**。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 一致→排除 KV** |
| 检测 | **检出** |
| 三层率 | **64 / 17 / 64**（触发 / 判坏 / 报告） |
| Detector | `token_repeat` |
| Origin | 见规格 |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) |
| 模型 | Qwen3-8B · TP2 · CARD=4,5 · util=0.35 · max-num-seqs=128 · `192.168.13.160` / `rg-test-160` |
| Run | `keep-set-retest-20261022` · `S10p-layers-20261023T121734` |

## 1 · 现象

约 17/64 被判坏；重复-token 检测命中。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 案例背景 / 构造

FullAttention 回收块未清零（`needs_kv_cache_zeroing` 被关掉一类路径）。细节见 [evidence/规格说明.md](./evidence/规格说明.md)。**「预期根因在 KV」≠ 本窗已证根因。**

## 3 · Guard 结果

**检出。** **64 / 17 / 64**。结案：**KV 一致→排除 KV**——有效槽有限、无数值崩溃；与干净对照的相似度全程 ≥0.99（见事实）。

## 4 · 复现技巧

| 项 | 怎么做 |
|----|--------|
| Overlay | `10_fullattn_recycle_zero.patch`（或生成脚本） |
| 负载 | 变长 pad · 并发 64 · 温度 0 · 搅动回收 |
| detector | `token_repeat` |
| 抓 dump | #19285；抓前清双树 |
| 对照 | 干净树上按 token id 原样重放 |

## 5 · 定界分析

### 事实

- **清洁标杆（≥2 组）：** 干净服务重放对照；**2 组**；shape 一致。对比窗口含**完整 prompt+生成**（不是只比了一截）；本窗约 `n_prompt=14`，`p+o−1`≈21。
- **两对同向：** 无数值问题；余弦全程干净（prompt 第 1 个 token 最差仍≈1.0）。
- **有效槽 / 格：** 有效槽有限、无数问题；没有「第一处余弦分叉」。
- **未用槽：** 异常侧有限非 0（**卫生**）；一对标杆未用槽也可能有限非 0——不单独当成坏结果原因。
- **读法：** 构造预期像「回收块脏 KV」，但本窗对账匹配 → 结案是**排除 KV 主因**（就本窗、本 head、对上的层而言）。
- 证据：`evidence/kv_*.json`；`verified_kv/S10p/`（**.pt 未入库**）。



### KV 对账表

分桶（可读性）：`≈1`≥0.99；`0.9–0.99`；`0.8–0.9`；`0.6–0.8`；`0.3–0.6`；`0.1–0.3`；`<0.1`（含负值）；数值门闩写清子类型（如 `数值问题:全零(zero_norm)` / `数值问题:NaN` / `数值问题:Inf`），勿只写「数值异常」（不编余弦）。

数据来自 `evidence/kv_v516_numeric_first.json`（及同结构字段）；不编造未入库 `.pt` 上的数。

两对同向时只展示**代表对**（对 1）。

**代表对**（`req_id`=`cmpl-95a5d11f50558864-0-9a4c6512`；对比窗 **21** token，其中 prompt **14**）。

**表1 · 每 token 最差格**（该 token 上差距最大的层；有数值门闩则整格写清子类型）

| token 序号 | 角色 | 该 token 最差格 |
| --- | --- | --- |
| 0 | prompt[0] | ≈1（最差 layer_67） |
| 1 | prompt[1] | ≈1（最差 layer_61） |
| 2 | prompt[2] | ≈1（最差 layer_67） |
| 3 | prompt[3] | ≈1（最差 layer_61） |
| 4 | prompt[4] | ≈1（最差 layer_69） |
| 5 | prompt[5] | ≈1（最差 L33） |
| 6 | prompt[6] | ≈1（最差 layer_71） |
| 7 | prompt[7] | ≈1（最差 layer_61） |
| 8 | prompt[8] | ≈1（最差 layer_63） |
| 9 | prompt[9] | ≈1（最差 layer_69） |
| 10 | prompt[10] | ≈1（最差 L33） |
| 11 | prompt[11] | ≈1（最差 layer_61） |
| 12 | prompt[12] | ≈1（最差 layer_71） |
| 13 | prompt[13] | ≈1（最差 layer_63） |
| 14 | out[0] | ≈1（最差 layer_63） |
| 15 | out[1] | ≈1（最差 layer_61） |
| 16 | out[2] | ≈1（最差 layer_63） |
| 17 | out[3] | ≈1（最差 layer_61） |
| 18 | out[4] | ≈1（最差 layer_63） |
| 19 | out[5] | ≈1（最差 layer_63） |
| 20 | out[6] | ≈1（最差 layer_63） |

**表2 · 首 token 逐层剖面（合并区间）** — 首 token = **prompt[0] / window token0**（与证据 `token_idx=0` 一致）。

| 层区间（model.layers） | 余弦 / 状态 |
| --- | --- |
| L0–L35 | ≈1 |

注：证据 `clean_model_tok0_cos` 仅存前 12 层抽样且均为 ≈1；首 token 全层最差仍 ≥0.99（L13）→ 合并为 L0–L35 ≈1。

### 推断

- 对账匹配 → **排除「坏值经/进 KV」为主因**（本窗）。
- 异常仍被检出 → 更可能在未对比到的路径；**不能**只凭本窗相似度把根因钉在 recycle-zero。

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
