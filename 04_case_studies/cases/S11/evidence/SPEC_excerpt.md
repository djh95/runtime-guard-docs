# S11 — MLA prefill RoPE pad misalignment

| 字段 | 值 |
|------|-----|
| **ID** | S11 |
| **Origin** | `ascend-only` |
| **Priority** | P0 |
| **KV?** | 间接（RoPE vs KV 长度 / pad 对齐） |
| **Guard pin** | G2 `f2aefd068` |
| **repro_mode** | `origin_tuned` |
| **difficulty** | `easy` |

## Origin 说明

Ascend strided MLA PROLOG_V3 / prefill RoPE 在 graph padding 下曾把 **含 pad 的 cos/sin** 直接喂给实际 token 长度的 query（[ascend#18798](https://github.com/vllm-project/vllm-ascend/pull/18798)）。修复是 slice 到 `num_prefill_tokens`。本场景对 pin 上已有的 `mla_preprocess_prefill` 路径做 **逆修复**：合成 pad 行后取 **pad-tail** 对齐（batch 维匹配，避免 InterleaveRope 硬崩；错位值忠于原 bug class）。禁止 NaN / fill。

## Upstream anchors

- https://github.com/vllm-project/vllm-ascend/pull/18798

## Overlay

[`patches/README.md`](./patches/README.md)

## Trigger / knobs / forbidden

1. **Trigger:** `ANOMALY_TRIGGER S11 mla_rope_pad` (query/kv) when pad-tail applied.
2. **Allowed knobs:** MLA model; concurrent var-len prefill; util / max-len / seqs; no-APC; synth pad rows when tables already actual-sized.
3. **Forbidden:** force NaN / token fill.

## 模型

`DeepSeek-V2-Lite`（MLA，proven）。

## Latest result

**PASS** `138 / 39 / 60` (`token_repeat`) — run `T190840` @ 160 `4,5`, DeepSeek-V2-Lite bf16. Evidence: [`../fail-evidence/S11/`](../fail-evidence/S11/).

## Expected detector

`token_repeat` 和/或 `logits_finite`。

## Origin-faithful protocol

See [`../PRINCIPLES.md`](../PRINCIPLES.md).

…（全文在私有 test 仓历史；本包以上表+FE 为准）
