# S07 — 量化 / scale 崩溃（amax / OOB scale）

| 字段 | 值 |
|------|-----|
| **ID** | S07 |
| **Origin** | `both` |
| **Priority** | P0 |
| **KV?** | 常连带 KV quant |
| **Guard pin** | G2 `f2aefd068` |
| **repro_mode** | `origin_tuned` |
| **difficulty** | `easy` |

## Origin 说明

上游 padding NaN 吃进 per-tensor amax、OOB scale、错误 metadata 继承等同族问题（[#37442](https://github.com/vllm-project/vllm/pull/37442) 链及相关 quant PR）。Ascend W8A8 / FP8 路径同样依赖 scale；短名单已证明 W8A8 可起服，FP8 当前 **不能跑** → 本场景以 **W8A8** 为主、FP8 标 backlog。失败模式共享，因此标 **`both`**。

## 上游锚点

- https://github.com/vllm-project/vllm/pull/37442
- Related quant/scale families in vLLM research freeze（§2.2 plan）

## Overlay

脏 padding + 量化路径；或损坏 scale 张量。细节见 [`patches/README.md`](./patches/README.md)。

## ≤5min 复现配方

1. `Qwen3-8B-W8A8` TP2（双机配对 / 单节点均 PASS）。
2. 大 pad + 单真实请求；循环 decode。
3. 盯 `logits_finite` 与算子错误日志。

## 模型

`Qwen3-8B-W8A8`、`DeepSeek-V2-Lite-W8A8`、`Qwen3-30B-A3B-W8A8`。**不用** FP8/DFlash（选型：当前不能跑）。

## Expected detector

`logits_finite`；若 dump 覆盖到，scale 区域可能异常。

## Success / gap

- Success = `logits_finite` / dump 触发。
- Gap：精度掉点但有限、无非有限值 → FAIL/gap。

## Repro rate

更细的历史配方不在本仓；本包以上表与归档证据为准。
