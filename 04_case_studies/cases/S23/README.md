# S23 · 一层 o_proj 权重置零（KV 不一致→定界）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 不一致→定界** |
| 检测 | **检出** |
| 三层率 | **2 / 16 / 48**（`token_repeat`×48） |
| Detector | `token_repeat`（threshold=8） |
| Origin | `both`（constructed weight-fault） |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) |
| 模型 | Qwen3-8B · TP2 · CARD=4,5 · `192.168.13.160` / `rg-test-160` |
| Run | 英文河名短句 × 48；`keep-set-retest-20261022` |

## 1 · 现象

部分请求塌成 `1.1.1…` / `0.1.0…` 复读（precision=16/48）；`token_repeat` 全检出。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 案例背景 / 构造

Post-load 置零一层 `o_proj.weight`（always-on）。细节见 [evidence/规格说明.md](./evidence/规格说明.md)。**构造根因在权重，不是本包 KV 已证「KV 子系统根因」。**

## 3 · Guard 结果

**检出。** **2 / 16 / 48**（注入几乎不打 trigger 日志，但输出复读仍被 `token_repeat` 抓住）。结案：**KV 不一致→定界**。

## 4 · 复现技巧

| 项 | 现行 |
|----|------|
| Overlay | `gen_s23_overlay.py` |
| Prompt | `Name one famous river… id={i}.` ×48 |
| detector | `token_repeat` thresh=8 |
| 配置 | boot READY 后须**重写** `runtime_config`（防 worker persist 覆写关检） |
| 抓 dump | #19285；清 kvcache |

## 5 · 定界分析

### 事实

- 三层 **2 / 16 / 48**；detector `token_repeat`×48。
- ≥2 组异常↔清洁标杆（标杆未亮 `logits_finite`）；shape 一致；history `p+o-1`（21 / 20）。
- 有效槽**有限**（无 Inf/NaN）；未用槽有限非 0 → **卫生**（通常不致坏结果）。
- 余弦：两组最低约 0.68；首个不一致都在 prompt 第 2 个 token、`model.layers.35`（脚本层定位；权重注入可解释为算子写出污染 KV，**勿**升格成「根因=第 35 层」）。

### 推断

- 对账不匹配 → **重开 KV 线**（坏值已进/经 KV）。
- 构造为权重故障；KV 不一致与「权重写出污染」相容，**不能**从本包推出具体 weight 名已证。

### 结论

- 结案档：**KV 不一致→定界**。
- 尚未定界到构造根因算子/提交；分析不出 / 证据不足。

## 6 · 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 静态补丁 |
| `evidence/规格说明.md` | 复现规格 |
| `evidence/三层计数.json` | 三层 |
| `evidence/跑批结果.json` | 跑批+结案摘要 |
| `evidence/samples/` | 样本 |
| `evidence/reports/` | 钉点 report |
| `evidence/kv_compare.json` | 两组余弦摘要 |
| `evidence/kv_finite_unused.json` | 有限性/未用槽分级 |

## 7 · 上游 PR 关系

构造 weight-fault 类；无单独上游「修复本 overlay」PR。#19285 仅抓 dump 辅助。
