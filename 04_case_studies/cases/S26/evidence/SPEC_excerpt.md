# S26 — RMSNorm weight multiply in fp32 (soft-inverse vLLM#42379)

| 字段 | 值 |
|------|-----|
| **ID** | S26 |
| **Origin** | `both` |
| **Priority** | P0 |
| **KV?** | no |
| **Guard pin** | G2 `f2aefd068` |
| **repro_mode** | `origin_tuned` |
| **difficulty** | `easy` |

## Origin 说明

[vLLM#42379](https://github.com/vllm-project/vllm/pull/42379) (2026-05): RMSNorm kernels multiplied `(x * rsqrt * w)` all in fp32 then cast; correct is `(x*rsqrt).to(w.dtype)*w`. ~3e-2/elem compounds across many norms → near-total token mismatch.

**Soft-inverse on Ascend:** replace `AscendRMSNorm.forward_oot` `npu_rms_norm` with the buggy fp32-mul formula. Fills **dtype/cast** gap. ≠ MoE / S14 / S20.

## Upstream anchors

- https://github.com/vllm-project/vllm/pull/42379

## Overlay

[`patches/README.md`](./patches/README.md) · [`../scripts/gen_s26_overlay.py`](../scripts/gen_s26_overlay.py)

## Trigger / knobs / forbidden

1. **Trigger:** `ANOMALY_TRIGGER S26 rmsnorm_fp32_mul`
2. **Allowed knobs:** Qwen3-8B; longer decode; concurrency; dtype fp16/bf16
3. **Forbidden:** force-NaN; token `fill_`

## 模型

`Qwen3-8B`.

## Expected detector

`token_repeat` preferred; weak `logits_finite` possible.

## Origin-faithful protocol

See [`../PRINCIPLES.md`](../PRINCIPLES.md). Three-layer rates required.

## Latest result

…（全文在私有 test 仓历史；本包以上表+FE 为准）
