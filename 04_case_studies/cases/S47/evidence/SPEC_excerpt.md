# S47 — K/V swap before attention

| 字段 | 值 |
|------|-----|
| **ID** | S47 |
| **Origin** | `both` (constructed swapped-KV) |
| **Priority** | P0 |
| **repro_mode** | `origin_tuned` |
| **difficulty** | `easy` |

## Origin
Swap `key, value` before `reshape_and_cache` / FA. Soft-inverse of correct KV assignment. ≠ S34/S35/S41.

## Overlay
[`../scripts/gen_s47_overlay.py`](../scripts/gen_s47_overlay.py)

## Trigger / knobs / forbidden
1. **Trigger:** `ANOMALY_TRIGGER S47 kv_swap`
2. **Allowed:** Qwen3-8B; concurrency
3. **Forbidden:** force-NaN; token `fill_`

## Model
`Qwen3-8B`

## Expected detector
`token_repeat` / `logits_finite`

…（全文在私有 test 仓历史；本包以上表+FE 为准）
