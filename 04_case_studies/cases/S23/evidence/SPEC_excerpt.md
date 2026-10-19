# S23 — Weight layer corruption (post-load zero/permute)

| 字段 | 值 |
|------|-----|
| **ID** | S23 |
| **Origin** | `both` (constructed; weight-fault class) |
| **Priority** | P0 |
| **KV?** | no (weights) |
| **Guard pin** | G2 `f2aefd068` |
| **repro_mode** | `origin_tuned` (minimal construct) |
| **difficulty** | `easy` (always-on) |

## Origin 说明

Post-load **weight corruption** class: after `load_model`, zero (or permute) one transformer layer weight so every forward produces garbage / collapsed tokens. Distinct from KV/slot/sampler families. Skills detect-only (no localization required).

Not an amplifier of detector symptoms (no NaN/`fill_` token writes) — mutates **weights** once at boot.

## Upstream anchors

- Weight-fault / bad-checkpoint class (constructed always-repro for Guard detect coverage)
- Complementary to runtime numeric bugs (S20) and quant scale (S07/S24)

## Overlay

[`patches/README.md`](./patches/README.md) · [`../scripts/gen_s23_overlay.py`](../scripts/gen_s23_overlay.py)

Hook Ascend `GPUModelRunner.load_model`: after `super().load_model`, zero `model.layers[L].self_attn.o_proj.weight` (fallback: first `*.weight` with dim≥2). Log `ANOMALY_TRIGGER S23`.

## Trigger / knobs / forbidden

1. **Trigger:** `ANOMALY_TRIGGER S23 weight_layer_corrupt`
2. **Allowed knobs:** layer index `L` (default mid-stack); zero vs row-permute; Qwen3-8B TP2
3. **Forbidden:** per-step NaN/`fill_` into logits/KV; force detector reports

## 模型

`Qwen3-8B` (bf16/fp16). Always-on after boot.

## Expected detector

`token_repeat` (and/or `logits_finite` if Inf/NaN appears). Always-repro once armed.

## Origin-faithful protocol


…（全文在私有 test 仓历史；本包以上表+FE 为准）
