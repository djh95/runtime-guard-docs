# S26 — RMSNorm weight multiply in fp32（soft-inverse vLLM#42379）

| 字段 | 值 |
|------|-----|
| **ID** | S26 |
| **Origin** | `both` |
| **Priority** | P0 |
| **KV?** | 否 |
| **Guard pin** | G2 `f2aefd068` |
| **repro_mode** | `origin_tuned` |
| **difficulty** | `easy` |

## Origin 说明

[vLLM#42379](https://github.com/vllm-project/vllm/pull/42379)（2026-05）：RMSNorm kernels 把 `(x * rsqrt * w)` 全在 fp32 里乘完再 cast；正确写法是 `(x*rsqrt).to(w.dtype)*w`。约 3e-2/elem 的误差跨多层会叠成近乎全错 token。

**Ascend soft-inverse：** 把 `AscendRMSNorm.forward_oot` 的 `npu_rms_norm` 换成错误的 fp32-mul 公式。补齐 **dtype / cast** 缺口。不等于 MoE / S14 / S20。

## 上游锚点

- https://github.com/vllm-project/vllm/pull/42379

## Overlay

见 [`patches/README.md`](./patches/README.md)。

## Trigger / knobs / forbidden

1. **Trigger：** `ANOMALY_TRIGGER S26 rmsnorm_fp32_mul`
2. **Allowed knobs：** Qwen3-8B；更长 decode；concurrency；dtype fp16/bf16
3. **Forbidden：** force-NaN；token `fill_`

## 模型

`Qwen3-8B`。

## Expected detector

优先 `token_repeat`；`logits_finite` 可能偏弱。

## Origin-faithful protocol

需要记三层率。更细的历史配方不在本仓；本包以上表与归档证据为准。
