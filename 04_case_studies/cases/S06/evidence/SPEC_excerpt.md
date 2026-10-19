# S06 — MoE 路由错误（bias dtype / padding mask）

| 字段 | 值 |
|------|-----|
| **ID** | S06 |
| **Origin** | `both` |
| **Priority** | P0 |
| **KV?** | 否（专家选择） |
| **Guard pin** | G2 `f2aefd068` |
| **repro_mode** | `origin_tuned` |
| **difficulty** | `easy` |

## Origin 说明

上游 TRT-LLM per-block FP8 MoE routing bias dtype 曾导致 DeepSeek-R1 精度断崖（[#38989](https://github.com/vllm-project/vllm/pull/38989)）；PCP MoE padding mask 错位（[#60946](https://github.com/vllm-project/vllm/pull/60946)）。Ascend 内核不同，但「错误 router bias / mask → 错专家」失败模式可共享，用 Ascend router 路径强制错误 dtype / mask 模拟 → **`both`**（类比，非 bit-exact CUDA 复现）。

## Upstream anchors

- https://github.com/vllm-project/vllm/pull/38989
- https://github.com/vllm-project/vllm/pull/60946

## Overlay

对 Ascend MoE router 强制错误 bias dtype，或 PCP≠1 时使用 #60946 逆逻辑。见 [`patches/README.md`](./patches/README.md)。

## ≤5min 复现配方

1. 小 MoE：`DeepSeek-V2-Lite` / `Qwen3-30B-A3B`（短名单）；固定 seed。
2. Overlay 后对照 run（同一 prompt）。
3. 严重时盯 `logits_finite` / `token_repeat`；Expect Guard **弱覆盖**。

## 模型

`DeepSeek-V2-Lite`、`Qwen3-30B-A3B` / `-W8A8`（proven）。

## Expected detector

间接：`token_repeat` 或 `logits_finite`。**无路由专用 detector。**

## Success / gap

- Success = 任一现有 detector 触发。
- Gap：输出崩但无 NaN/无重复 → **FAIL/gap**（典型；留给路由类新算法）。不得用 GSM8K 顶替 pass。

## Repro rate

…（全文在私有 test 仓历史；本包以上表+FE 为准）
