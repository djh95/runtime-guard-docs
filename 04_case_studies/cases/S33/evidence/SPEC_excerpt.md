# S33 — Incomplete final-logit softcap

| 字段 | 值 |
|------|-----|
| **ID** | S33 |
| **Origin** | `both` (constructed softcap class) |
| **Priority** | P0 |
| **repro_mode** | `origin_tuned` |
| **difficulty** | `easy` |

## Origin
Softcap / `final_logit_softcapping` class ([vLLM#56579](https://github.com/vllm-project/vllm/pull/56579) family; Gemma `final_logit_softcapping`). Soft-inverse of correct softcap: `÷cap + tanh` but **skip `*cap` rescale**. Forces cap=30 when model has none (boot set). ≠ S20 (unstable exp/tanh Inf/Inf on V2 sampler).

## Overlay
[`../scripts/gen_s33_overlay.py`](../scripts/gen_s33_overlay.py)

## Trigger / knobs / forbidden
1. **Trigger:** `ANOMALY_TRIGGER S33 softcap_incomplete`
2. **Allowed:** Qwen3-8B; concurrency
3. **Forbidden:** force-NaN; token `fill_`

## Model
`Qwen3-8B` (or Gemma4 when softcap-native preferred)

## Expected detector
`token_repeat`
**PASS** 132/15/48 @ 160 cards 8,9 (`33_softcap_incomplete-20261017T130612`).

…（全文在私有 test 仓历史；本包以上表+FE 为准）
