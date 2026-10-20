# S25 — RoPE second-half write drop（soft-inverse ascend#7082）

| 字段 | 值 |
|------|-----|
| **ID** | S25 |
| **Origin** | `ascend-only` |
| **Priority** | P0 |
| **KV?** | 否（RoPE） |
| **Guard pin** | G2 `f2aefd068` |
| **repro_mode** | `origin_tuned` |
| **difficulty** | `easy` |

## Origin 说明

[ascend#7082](https://github.com/vllm-project/vllm-ascend/pull/7082)（2026-03）：Triton `rope_siso` 算完后半旋转 tile，却 **从未 `tl.store`** → neox Q/K residual dims 留在 pre-rotate → 精度塌 / 非 neox 上 UB overflow。

**在 Ascend G2 热路径上做 soft-inverse**（热路径是 `npu_rotary_embedding`，不是 Triton）：rotary 之后，把 `query/key[..., rotary_dim//2:rotary_dim]` 恢复成 pre-rotate 值——同一套 missing-store 逻辑。不等于 S11（pad 长度）。

## 上游锚点

- https://github.com/vllm-project/vllm-ascend/pull/7082

## Overlay

见 [`patches/README.md`](./patches/README.md)。

## Trigger / knobs / forbidden

1. **Trigger：** `ANOMALY_TRIGGER S25 rope_siso_half_drop`
2. **Allowed knobs：** Qwen3-8B TP2；concurrency；`max-model-len`；util
3. **Forbidden：** force-NaN；token `fill_`

## 模型

`Qwen3-8B`（neox-style full RoPE）。

## Expected detector

`token_repeat`（和 / 或 `logits_finite`）。

## Origin-faithful protocol

需要记三层率。更细的历史配方不在本仓；本包以上表与归档证据为准。
