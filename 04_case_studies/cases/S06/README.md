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

**PASS。** `status.json` 写 `detect_reports=0`，但同一次归档已留下 `reports/report_*.json`（`incident_type=token_repeat`）。对外以 PASS + 归档报告为准，并记下 status 字段曾滞后。

## 4 · 复现

按 pin / 模型 / overlay 对齐三层率。历史上有过 setup BLOCKED（缺 `aclnnAddRmsNormBias` 或 MoE OOM）——见 `evidence/BLOCKED.historical.md`，那不是 FAIL。标杆是已跑通的 162 归档。

## 5 · 别人按包能核对什么

MoE 饱和类不在对外保留案例刷分；这一例只作路由模版。「KV 数值看起来正常」不等于 MoE 类问题已排除干净。
