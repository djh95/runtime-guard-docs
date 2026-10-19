# S45 — Top-k/top-p direction flip (bottom nucleus)

| 字段 | 值 |
|------|-----|
| **ID** | S45 |
| **Origin** | `both` (constructed wrong-topk-direction) |
| **Priority** | P0 |
| **repro_mode** | `origin_tuned` |
| **difficulty** | **FAIL** (detect miss) |

## Origin
Apply top-k/top-p on `-logits` then negate back — keeps lowest-k / inverted nucleus. Soft-inverse of comparison direction. **Not** an amplifier.

## Status
**FAIL+GAP** — trigger fires; unique-garbage precision; `detect=0` (no local re-reads / nonfinite). Parked; do not treat as PASS / do not amplifier-retune. See S46 for sampling soft-inv that detects. Evidence: `WHY_UNDETECTED.md` + ≥3 samples.

## Overlay
[`../scripts/gen_s45_overlay.py`](../scripts/gen_s45_overlay.py)

## Trigger / knobs / forbidden
1. **Trigger:** `ANOMALY_TRIGGER S45 topk_bottom_keep`
2. **Allowed:** Qwen3-8B; `top_k`; concurrency
3. **Forbidden:** force-NaN; token `fill_`; logits.zero_

## Model
`Qwen3-8B`

## Evidence
[`../fail-evidence/S45/`](../fail-evidence/S45/) (`WHY_FAIL.md`)

…（全文在私有 test 仓历史；本包以上表+FE 为准）
