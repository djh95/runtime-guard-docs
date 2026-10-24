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
- **清洁标杆（≥2 组）：** 干净服务重放对照；标杆**未**亮 `logits_finite`；shape `[1,128,4,128]`。钉点 report：prompt=14，**`output_at_dump=1`（o=1）**，history 按 `p+o−1` 长度为 14。
- **两对同向（有限性，不定层）：** 异常侧**有效槽全是 NaN**（无 Inf）；**未用槽也有 NaN**（严重，不是「仅有限非 0 的卫生脏写」）。标杆侧有效槽有限、未用槽全 0。
- **为何不定「第一坏层」：** 余弦要两边都是可比较的有限数。有效槽已是 NaN → **没有有效余弦格**，不能写「第几层先分叉」。短生成窗（o=1）也削弱层定位。
- 证据：`evidence/kv_compare.json`、`kv_finite_unused.json`；`verified_kv/S48/`（**.pt 未入库**）。

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
