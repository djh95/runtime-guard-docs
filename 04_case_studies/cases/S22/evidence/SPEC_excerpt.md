# S22 — Spec residual resample RNG collide (no SALT)

| 字段 | 值 |
|------|-----|
| **ID** | S22 |
| **Origin** | `ascend-only` (+ cousin [vLLM#61161](https://github.com/vllm-project/vllm/pull/61161)) |
| **Priority** | P0 |
| **KV?** | draft KV present (spec) |
| **Guard pin** | G2 `f2aefd068` |
| **repro_mode** | `origin_tuned` |
| **difficulty** | `easy`–`medium` (detect may be distributional → FAIL+GAP risk) |

## Origin 说明

Rejection verification and residual categorical resample share the same RNG `(seed, position)`. Without an independent salt, recovered tokens after rejection are **biased** (e.g. always token 2 for a one-hot draft on 0 with target `[0.5,0.25,0.25]`) — [ascend#18657](https://github.com/vllm-project/vllm-ascend/pull/18657).

**G2 pin already lacks `RESAMPLE_NOISE_SALT`** (fix is main/0.30.0 backport only). Overlay adds trigger logging on the residual resample entry; does **not** invent NaN/`fill_`. Distinct from S05 (NaN argmax / uniform 0) and S20 (softcap overflow).

## Upstream anchors

- https://github.com/vllm-project/vllm-ascend/pull/18657
- https://github.com/vllm-project/vllm/pull/61161

## Overlay

[`patches/README.md`](./patches/README.md) · [`../scripts/gen_s22_overlay.py`](../scripts/gen_s22_overlay.py)

## Trigger / knobs / forbidden

1. **Trigger:** `ANOMALY_TRIGGER S22 spec_resample_rng_collide`
2. **Allowed knobs:** eagle3 + `temperature>0`; `num_speculative_tokens`; concurrency; seeds
3. **Forbidden:** force NaN; token `fill_`; invent SALT then remove on a fixed tree without documenting pin state

## 模型

`Qwen3-8B` + `/mnt/weight/Qwen3-8B-speculator.eagle3` (S05-proven boot on G2).

## Expected detector

`token_repeat` / `spec_acceptance` if bias is strong; else **FAIL+GAP** with recovered-token histogram + samples (distributional).

## Origin-faithful protocol

See [`../PRINCIPLES.md`](../PRINCIPLES.md).


…（全文在私有 test 仓历史；本包以上表+FE 为准）
