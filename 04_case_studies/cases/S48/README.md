# S48 · Residual 取反（KV 不一致→定界）

公开案例包。融合 add-RMSNorm 前把 residual 乘 −1。输出全是 `!!!!…`；专抓「logits 非有限」的检测 48/48 命中；KV 有效槽全是 NaN → **KV 不一致**，但**不能**用相似度指出第一坏层。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 不一致→定界**（靠有限性，不是余弦定层） |
| 检测 | **检出** |
| 三层率 | **44 / 48 / 48**（触发 / 判坏 / 报告；全是 `logits_finite`） |
| Detector | `logits_finite`（logits 里出现 NaN/Inf） |
| Origin | `both` |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) |
| 模型 | Qwen3-8B · TP2 · CARD=4,5 |
| Run | `keep-set-retest-20261022` · `S48-layers-20261023T103724` / `S48-pr19285-20261023T103909` / `S48-ref-recap-20261023T104049` |

## 1 · 现象

全请求 `!!!!…`（48 条彼此相同）；采样前 logits 非有限。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 案例背景 / 构造

反向注入：fused add-RMSNorm 前 `residual = -residual`。细节见 [evidence/规格说明.md](./evidence/规格说明.md)。**构造根因不是本包 KV 已证。**

## 3 · Guard 结果

**检出。** **44 / 48 / 48**。结案：**KV 不一致→定界**——看有效槽/未用槽是否有限；**不是**「第几层余弦先分叉」那种定层（见事实）。

钉点报告：prompt 长度 14；dump 时只生成了 1 个 token（很短）。

## 4 · 复现技巧（必读）

| 项 | 怎么做 |
|----|--------|
| Overlay | `gen_s48_overlay.py` |
| Prompt | 英文河名短句 ×48 |
| detector | `logits_finite` |
| 抓 dump | 非空 prompt token 列表 → 临时 #19285；抓前清 kv cache |
| 对照 | **干净树、无 overlay**；确认对照**未**亮 `logits_finite`；手动 dump + 按 token id 重放 |

## 5 · 定界分析

### 事实

- **现象与检测：** 全请求 `!!!!…`；`logits_finite` 48/48 命中。三层 **44 / 48 / 48**。
- **清洁标杆（≥2 组）：** 干净服务重放对照；标杆**未**亮 `logits_finite`；shape `[1,128,4,128]`。钉点 report：prompt=14，**`output_at_dump=1`（输出只有 1 个 token）**，history 按「prompt 长度 + 输出长度 − 1」 长度为 14。
- **两对同向（有限性，不定层）：** **有效槽：** 异常侧全是 NaN（无 Inf）→ 数值问题主证据。**未用槽：** 异常侧亦有 NaN（严重，不是「仅有限非 0 的卫生脏写」）；标杆侧有效有限、未用全 0（`kv_finite_unused.json`）。分写两边，**勿**把未用说成「一定填 0」。
- **为何不定「第一坏层」：** 余弦要两边都是可比较的有限数。有效槽已是 NaN → **没有有效余弦格**，不能写「第几层先分叉」。短生成窗（输出只有 1 个 token）也削弱层定位。
- 证据：`evidence/kv_compare.json`、`kv_finite_unused.json`；`verified_kv/S48/`（**.pt 未入库**）。



### KV 对账表

分桶（可读性）：`≈1`≥0.99；`0.9–0.99`；`0.8–0.9`；`0.6–0.8`；`0.3–0.6`；`0.1–0.3`；`<0.1`（含负值）；数值问题写清子类型（如 `数值问题:全零(zero_norm)` / `数值问题:NaN` / `数值问题:Inf`），勿只写「数值异常」（不编余弦）。

数据来自 `evidence/kv_compare.json`（有效槽全 NaN；无余弦）。代表对 `cmpl-848bd82c5c4916d7-0-994caee4`。  
注：`output_at_dump=1` → history 止于 prompt；**本包对比窗无后续 out**（非表1 省略）。

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

**表2 · 首个出问题的 token 的逐层剖面（合并区间）** — **首个出问题的 token = prompt[0]**（有效槽自 token0 起全 NaN）。

| 层区间（model.layers） | 余弦 / 状态 |
| --- | --- |
| L0–L35 | 数值问题:NaN |

注：证据有效槽全 NaN（无 Inf）；未用槽亦有 NaN；自 prompt[0]、L0–L35；不定层、无余弦。

### 推断

- 有效槽全 NaN → **KV 已坏**；不能写「第一坏层」。
- 不能单凭此证「根因=residual 取反」算子名。

### 结论

- 结案档：**KV 不一致→定界**（有限性；两组同向）。

## 6 · 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 补丁 |
| `evidence/规格说明.md` | 规格 |
| `evidence/三层计数.json` / `跑批结果.json` | 三层 / 摘要 |
| `evidence/samples/` / `reports/` | 样本 / 报告 |
| `evidence/kv_*.json` | 对账 / 有限性 |

## 7 · 上游 PR 关系

构造型反向注入；#19285 仅抓 dump 辅助。
