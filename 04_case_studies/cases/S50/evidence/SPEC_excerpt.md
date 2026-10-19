# S50 — SwiGLU gate/up half-swap

| 字段 | 值 |
|------|-----|
| **ID** | S50 |
| **Origin** | `both` (constructed swapped-SwiGLU-halves) |
| **Priority** | P0 |
| **repro_mode** | `origin_tuned` |
| **difficulty** | `easy` |

## Origin
`cat(up, gate)` then `npu_swiglu`. Soft-inverse of correct gate/up order. ≠ S39 skip-silu. No force-write.

## Overlay
[`../scripts/gen_s50_overlay.py`](../scripts/gen_s50_overlay.py)

## Trigger / knobs / forbidden
1. **Trigger:** `ANOMALY_TRIGGER S50 swiglu_swap_halves`
2. **Allowed:** Qwen3-8B; concurrency
3. **Forbidden:** force-NaN; token `fill_`; logits.zero_

## Model
`Qwen3-8B`

## Expected detector
`token_repeat` / `logits_finite`

…（全文在私有 test 仓历史；本包以上表+FE 为准）
