# S25 — RoPE second-half write drop (soft-inverse ascend#7082)

| 字段 | 值 |
|------|-----|
| **ID** | S25 |
| **Origin** | `ascend-only` |
| **Priority** | P0 |
| **KV?** | no (RoPE) |
| **Guard pin** | G2 `f2aefd068` |
| **repro_mode** | `origin_tuned` |
| **difficulty** | `easy` |

## Origin 说明

[ascend#7082](https://github.com/vllm-project/vllm-ascend/pull/7082) (2026-03): Triton `rope_siso` computed the second-half rotated tile but **never `tl.store`d** it → neox Q/K residual dims stayed pre-rotate → accuracy collapse / UB overflow on non-neox.

**Soft-inverse on Ascend G2 path** (hot path is `npu_rotary_embedding`, not Triton): after rotary, restore `query/key[..., rotary_dim//2:rotary_dim]` from pre-rotate values — same missing-store logic. ≠ S11 (pad length).

## Upstream anchors

- https://github.com/vllm-project/vllm-ascend/pull/7082

## Overlay

[`patches/README.md`](./patches/README.md) · [`../scripts/gen_s25_overlay.py`](../scripts/gen_s25_overlay.py)

## Trigger / knobs / forbidden

1. **Trigger:** `ANOMALY_TRIGGER S25 rope_siso_half_drop`
2. **Allowed knobs:** Qwen3-8B TP2; concurrency; `max-model-len`; util
3. **Forbidden:** force-NaN; token `fill_`

## 模型

`Qwen3-8B` (neox-style full RoPE).

## Expected detector

`token_repeat` (and/or `logits_finite`).

## Origin-faithful protocol

See [`../PRINCIPLES.md`](../PRINCIPLES.md). Three-layer rates required.

## Latest result

…（全文在私有 test 仓历史；本包以上表+FE 为准）
