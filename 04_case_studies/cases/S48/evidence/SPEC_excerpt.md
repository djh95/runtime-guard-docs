# S48 — Residual negated before add-RMSNorm

| 字段 | 值 |
|------|-----|
| **ID** | S48 |
| **Origin** | `both` (constructed wrong-residual-sign) |
| **Priority** | P0 |
| **repro_mode** | `origin_tuned` |
| **difficulty** | `easy` |

## Origin
`residual = -residual` before fused add-RMSNorm. Soft-inverse of residual polarity. ≠ S31 drop ≠ S38 skip. No force-write.

## Overlay
[`../scripts/gen_s48_overlay.py`](../scripts/gen_s48_overlay.py)

## Trigger / knobs / forbidden
1. **Trigger:** `ANOMALY_TRIGGER S48 residual_negate`
2. **Allowed:** Qwen3-8B; concurrency
3. **Forbidden:** force-NaN; token `fill_`; logits.zero_

## Model
`Qwen3-8B`

## Expected detector
`token_repeat` / `logits_finite`

…（全文在私有 test 仓历史；本包以上表+FE 为准）
