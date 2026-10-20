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

上游 TRT-LLM per-block FP8 MoE routing bias dtype 曾导致 DeepSeek-R1 精度断崖（[#38989](https://github.com/vllm-project/vllm/pull/38989)）；PCP MoE padding mask 错位（[#60946](https://github.com/vllm-project/vllm/pull/60946)）。Ascend 内核不同，但「错误 router bias / mask → 错专家」失败模式可以共享：在 Ascend router 路径上强制错误 dtype / mask 来模拟，因此标成 **`both`**（类比，不是 bit-exact CUDA 复现）。

## 上游锚点

- https://github.com/vllm-project/vllm/pull/38989
- https://github.com/vllm-project/vllm/pull/60946

## Overlay

对 Ascend MoE router 强制错误 bias dtype，或在 PCP≠1 时使用 #60946 的逆逻辑。细节见 [`patches/README.md`](./patches/README.md)。

## ≤5min 复现配方

1. 小 MoE：`DeepSeek-V2-Lite` / `Qwen3-30B-A3B`（短名单）；固定 seed。
2. Overlay 后做对照 run（同一 prompt）。
3. 严重时盯 `logits_finite` / `token_repeat`；预期 Guard **弱覆盖**。

## 模型

`DeepSeek-V2-Lite`、`Qwen3-30B-A3B` / `-W8A8`（已验证可跑）。

## Expected detector

间接：`token_repeat` 或 `logits_finite`。**没有路由专用 detector。**

## Success / gap

- Success = 任一现有 detector 触发。
- Gap：输出崩了但没有 NaN、也没有重复 → **FAIL/gap**（典型；留给路由类新算法）。不得用 GSM8K 顶替 pass。

## Repro rate

更细的历史配方不在本仓；本包以上表与归档证据为准。
