# S26 · RMSNorm fp32 错乘（KV 一致→排除 KV）

公开案例包。RMSNorm 权重在错误精度路径上相乘（反向注入）。输出 `1.1.1…` 复读被检出；KV 对账与干净对照对得上 → **排除 KV 主因**。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 一致→排除 KV** |
| 检测 | **检出** |
| 三层率 | **470 / 14 / 48**（触发可浮动；**报告 48/48**） |
| Detector | `token_repeat`（阈值=8） |
| Origin | 见规格 |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) |
| 模型 | Qwen3-8B · TP2 · CARD=4,5 · `192.168.13.160` / `rg-test-160` |
| Run | 英文河名短句 × 48 并发 + 阈值 8；`keep-set-retest-20261022` |

## 1 · 现象

反复数字串；重复检测命中。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 案例背景 / 构造

RMSNorm fp32 错乘路径（反向注入）。细节见 [evidence/规格说明.md](./evidence/规格说明.md)。

## 3 · Guard 结果

**检出。** **470 / 14 / 48**。结案：**KV 一致→排除 KV**（对比窗内相似度几乎为 1；见事实）。

## 4 · 复现技巧（必读）

| 项 | 怎么做 |
|----|--------|
| Overlay | `gen_s26_overlay.py` |
| Prompt | 英文河名短句 ×48 并发 |
| detector | `token_repeat` 阈值 8 |
| 抓 dump | 非空 prompt token 列表 → 临时 #19285 |

## 5 · 定界分析

### 事实

- **现象与三层：** 输出常成 `1.1.1…` / `1.0.0…` 复读；三层 **470 / 14 / 48**（`token_repeat` 检出 48）。样本见 `evidence/samples/`。
- **清洁标杆（≥2 组）：** 干净服务重放对照。钉点 report 均非空 prompt（#19285）：一组约 prompt=14、output=8，另一组 prompt=14、output=17。
- **对比窗口：** **`n_tokens = p + o − 1`**（两组分别为 21、30）。
- **两对同向（排除 KV）：** 对比窗内各层余弦最低仍 ≥0.999988；**没有**首个不一致；无全 NaN 崩溃。
- 服务器 dump：`verified_kv/S26/`（**.pt 未入库**）；包内摘要 `kv_compare.json`。

### 推断

- 对账匹配 → **排除 KV 主因**（本窗）。
- 复读仍在 → 更可能在 Norm/精度路径，而非本窗已匹配的 KV 槽。

### 结论

- 结案档：**KV 一致→排除 KV**。

## 6 · 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 补丁 |
| `evidence/规格说明.md` | 规格 |
| `evidence/三层计数.json` / `跑批结果.json` | 三层 / 摘要 |
| `evidence/samples/` / `reports/` | 样本 / 报告 |
| `evidence/kv_compare.json` | 对账摘要 |

## 7 · 上游 PR 关系

见规格。
