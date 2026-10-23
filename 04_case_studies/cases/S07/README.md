# S07 · W8A8 scale collapse（KV 不一致→定界 · 乱码漏检）

公开自洽案例包。**乱码出现了，但 logits 仍有限**，所以 `logits_finite` 没响（乱码漏检）；认乱码看 samples；异常 KV 靠后来的 `manual_dump`。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 不一致→定界**（数值门闩：有效槽范数全零） |
| 检测 | **乱码漏检**（期望 `logits_finite` → 0 report） |
| 三层率 | **74 / 48 / 0**（跨请求内容相同×48） |
| Detector | 期望 `logits_finite` → **miss** |
| Origin | 见规格 |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) |
| 模型 | Qwen3-8B-W8A8 · TP2 · CARD=4,5 · `192.168.13.160` / `rg-test-160` |
| Run | `keep-set-retest-20261022` · `S07-layers-20261023T123413` |

## 1 · 现象

跨请求内容相同的乱码×48（见 [evidence/samples/](./evidence/samples/)）。**无** detector report。

## 2 · 案例背景 / 构造

W8A8 dequant / scale 崩溃族。细节见 [evidence/规格说明.md](./evidence/规格说明.md)。

## 3 · Guard 结果

**乱码漏检。** **74 / 48 / 0**。异常 KV 靠 **`manual_dump`**（≥2 对）。结案档：**KV 不一致→定界**（v5.16：有效槽 **zero_norm** 自 token0 / model L0 起；无有效余弦格）。

## 4 · 复现技巧

| 项 | 现行复现 |
|----|----------|
| Overlay | `07_quant_scale_collapse.patch` |
| 模型 | Qwen3-8B-W8A8 |
| detector | `logits_finite`（预期 miss） |
| 抓 dump | `manual_dump` 水位递增 + #19285 |

## 5 · 定界分析

### 事实

- **≥2 组**清洁标杆；shape 一致；prompt 窗（`o=1`）。
- **v5.16（两对同向）：** 数值问题为有效槽范数全零（`zero_norm`），从 prompt 第 1 个 token、模型第 0 层起；dump 双名 `layer_36` = `model.layers.0`（dump 双名：`layer_36` 与 `model.layers.0` 指同一层，不是「第 36 层」。）；无有效余弦格。
- 有限性脚本：有效槽有限且范数为 0（全零）→ 走数值门闩，不算余弦。
- 证据：`evidence/kv_compare.json` + `kv_v516_numeric_first.json`（**.pt 未入库**）。

### 推断

- 有效槽全零范数 → **定界到数值问题（zero_norm）**；不定余弦层。
- 与「乱码漏检」并列：检测抓不住，对账仍可定界。

### 结论

- 结案档：**KV 不一致→定界**（数值门闩；两组同向）。
- 检测侧：**乱码漏检**。

## 6 · 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 补丁 |
| `evidence/规格说明.md` | 规格 + 实测 |
| `evidence/三层计数.json` | 三层 |
| `evidence/跑批结果.json` | 摘要 |
| `evidence/samples/` | 乱码样本 |
| `evidence/reports/` | `manual_trigger` |
| `evidence/kv_*.json` | 对账 / v5.16 / 有限性 |

## 7 · 上游 PR 关系

见规格（#37442 族）。
