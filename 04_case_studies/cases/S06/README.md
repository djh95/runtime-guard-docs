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

**PASS。** 以归档 `reports/report_*.json`（`token_repeat`）为准；`跑批结果.json` 的 `detect_reports=0` 与报告不一致时，以 report 为准。

**report 空 `prompt_token_ids`：** 本包归档 report 的 `prompt_token_ids` / `prompt_text` 为空——异步下检测和生成 report 在请求结束之后，prompt 已被清空（output 仍有）。**阅读**完整 prompt 文本看 [evidence/samples/](./evidence/samples/)；**tokenize / 定界标杆**须以实际捕获的 token ids 为准——本包当前无非空 `prompt_token_ids`，**不要**从 sample 字符串再 encode 补造；应修 Guard 捕获或从仍持有 ids 的路径重抓后再归档。通则见 [④ 名词表 · 标杆请求 / report 空 prompt](../../README.md#名词怎么读先看这里)。

## 4 · 复现技巧

按 pin / 模型 / overlay 对齐三层率。历史上有过 setup BLOCKED（缺 `aclnnAddRmsNormBias` 或 MoE OOM）——见 `evidence/BLOCKED.historical.md`，那不是 FAIL。标杆是已跑通的 162 归档。

## 5 · 教学要点

1. 本例只作 MoE 路由模版；饱和类不在对外保留案例刷分。
2. 核对时看 router / 专家相关 report 字段——KV 数值正常 ≠ MoE 已排除。

## 定界分析

1. **L1 detect 停点**——detect：`token_repeat` 命中（归档 report×1；以 report 为准）。
2. **L2 class-hint**——L2 class-hint：MoE 路由（bias/mask → 错专家）；KV finite ≠ 根因。
3. **标杆 / Q1–Q5**——无 buggy+ref 标杆 → Q1–Q5 不适用 / KV=未知。
4. **结合现象**——见 `evidence/samples/` · `evidence/reports/`。
5. **结案要点**——PASS；DeepSeek-V2-Lite；三层以 README 钉点为准。

## 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格（Origin / 锚点 / overlay / knobs / 期望 detector） |
| `evidence/三层计数.json` | 三层明细（trigger / precision / detect） |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/samples/` | prompt + completion 样本（**阅读 / 现象核对**；非 tokenize 标杆） |
| `evidence/reports/` | Guard detector 报告（本包归档 **`prompt_token_ids` 为空**：异步落盘后已清；阅读看 samples，标杆须另抓 ids；见上节与 [④ 名词表](../../README.md#名词怎么读先看这里)） |


## 上游 PR 关系

| PR / 链接 | 角色 |
|-----------|------|
| [vLLM#38989](https://github.com/vllm-project/vllm/pull/38989) | **根因类比**（MoE routing bias dtype） |
| [vLLM#60946](https://github.com/vllm-project/vllm/pull/60946) | **同族相关**（PCP MoE padding mask） |
