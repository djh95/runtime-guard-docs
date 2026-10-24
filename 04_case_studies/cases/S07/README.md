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

**乱码漏检。** **74 / 48 / 0**。异常 KV 靠 **`manual_dump`**（≥2 对）。结案档：**KV 不一致→定界**（v5.16：有效槽从 prompt 第 1 个 token、模型第 0 层起即为全零；无有效余弦格——见下节）。

## 4 · 复现技巧

| 项 | 现行复现 |
|----|----------|
| Overlay | `07_quant_scale_collapse.patch` |
| 模型 | Qwen3-8B-W8A8 |
| detector | `logits_finite`（预期 miss） |
| 抓 dump | `manual_dump` 水位递增 + #19285 |

## 5 · 定界分析

### 事实

- **清洁标杆（≥2 组）：** 用同一段 history，在**未打 overlay 的干净服务**上重放，抓到的 KV 当作对照。本包成对 **2 组**；两边张量 shape 一致（`[1,128,4,128]`）。抓 dump 时生成很短：报告里 `output_token_count=1`（常写作 **`o=1`**），可比长度主要是 prompt（本窗 `n_prompt=14`，history 按 `p+o−1` 也是 14 个 token）。
- **两对同向：** 下面说的数值结论在 **两对异常↔标杆** 上相同，不是一对有、一对没有。
- **有效槽 / 「格」：** 有效槽 = 当前请求真正用到的 KV 位置；对账时「某一个 token × 某一层」算一格。本窗从 prompt 第 1 个 token 起，异常侧有效槽就被判成数值问题。
- **数值门闩（`zero_norm`）：** 有限性检查发现：这些有效槽里的数都是有限的（不是 NaN/Inf），但 **整段范数 = 0**，也就是 **全是 0**。脚本把这种「有限但全零」标成 `数值问题:zero_norm`，并优先用它定界，而不是再去算和标杆有多像。
- **为何不算余弦：** 余弦比较要两边都是「可比较的正常数值」。有效槽已经全零（数值问题），本窗统计里 **余弦格数 = 0**，所以 **没有**「第一处余弦分叉在哪一层」可写——不是漏算，是门闩挡住了。
- **dump 双名（为何 `layer_36` = `model.layers.0`，不是第 36 层）：** 同一次 dump 目录里并存两套文件名，各 36 个（合计 72）。一套叫 `model.layers.0…35.self_attn.attn`（模型层号）；另一套叫 `layer_36…71`。按编号一一对应：`layer_(36+i)` ↔ `model.layers.i`（例如 `layer_36`↔`model.layers.0`，`layer_37`↔`model.layers.1`）。对账脚本按名字排序时，会先碰到 `layer_36`，所以「全名首次数值问题」写在 `layer_36`；若只看 `model.layers.*`，同一事实落在 **`model.layers.0`**。两对都是：prompt token0 起即 `zero_norm`。
- 证据：`evidence/kv_compare.json`、`kv_v516_numeric_first.json`、`kv_finite_unused.json`（**.pt 未入库**；服务器 `verified_kv/S07/`）。

### 推断

- 有效槽全零 → **定界到数值问题（全零）**；本窗不能再用余弦指出「第一坏层」。
- 与「乱码漏检」并列：检测抓不住乱码，但对账仍能定界。

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
