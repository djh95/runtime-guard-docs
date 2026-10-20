# S06 · MoE routing bias / topk→0（PASS · 唯一公开 MoE）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
| 三层率 | **70 / 1 / report×1**（`status.layers.detect_reports=0` 与归档报告不一致，见正文） |
| Detector | `token_repeat` |
| Origin | `both` |
| Guard pin | G2 f2aefd068 |
| 模型 | DeepSeek-V2-Lite |
| Run | 06_moe_routing_bias-20261016T081459 @ 162 cards 0,1 |

## 1 · 现象

MoE 路由偏置或 mask 出错时，请求会进错专家。归档有 `token_repeat` 报告与 repeat 样本文。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 根因

错误 router bias / mask 类（非 bit-exact CUDA）。对外保留案例 **只留这一例** MoE。上游：[#38989](https://github.com/vllm-project/vllm/pull/38989)、[#60946](https://github.com/vllm-project/vllm/pull/60946)。

## 3 · Guard 结果

**PASS。** 以归档 `reports/report_*.json`（`token_repeat`）为准；`status.json` 的 `detect_reports=0` 与报告不一致时，以 report 为准。

## 4 · 复现

按 pin / 模型 / overlay 对齐三层率。历史上有过 setup BLOCKED（缺 `aclnnAddRmsNormBias` 或 MoE OOM）——见 `evidence/BLOCKED.historical.md`，那不是 FAIL。标杆是已跑通的 162 归档。

## 5 · 教学要点

1. 本例只作 MoE 路由模版；饱和类不在对外保留案例刷分。
2. 核对时看 router / 专家相关 report 字段——KV 数值正常 ≠ MoE 已排除。
