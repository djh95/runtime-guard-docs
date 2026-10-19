# S43 — Embedding scale blowup (×100)

| 字段 | 值 |
|------|-----|
| **ID** | S43 |
| **Origin** | `both` (constructed wrong-embed-scale) |
| **Priority** | P0 |
| **repro_mode** | `origin_tuned` |
| **difficulty** | `easy` |

## Origin
After embedding lookup, `mul_(100)`. Soft-inverse of correct embed magnitude. ≠ S23 weight-zero ≠ S41 attn-out.

## Overlay
[`../scripts/gen_s43_overlay.py`](../scripts/gen_s43_overlay.py)

## Trigger / knobs / forbidden
1. **Trigger:** `ANOMALY_TRIGGER S43 embed_scale_blowup`
2. **Allowed:** Qwen3-8B; concurrency
3. **Forbidden:** force-NaN; token `fill_`

## Model
`Qwen3-8B`

## Expected detector
`logits_finite` / `token_repeat`

…（全文在私有 test 仓历史；本包以上表+FE 为准）
