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

Ascend strided MLA PROLOG_V3 / prefill RoPE 在 graph padding 下，曾把 **含 pad 的 cos/sin** 直接喂给实际 token 长度的 query（[ascend#18798](https://github.com/vllm-project/vllm-ascend/pull/18798)）。修复是 slice 到 `num_prefill_tokens`。本场景对 pin 上已有的 `mla_preprocess_prefill` 路径做 **逆修复**：合成 pad 行后取 **pad-tail** 对齐（batch 维匹配，避免 InterleaveRope 硬崩；错位值忠于原 bug class）。禁止 NaN / fill。

## 上游锚点

- https://github.com/vllm-project/vllm-ascend/pull/18798

## Overlay

意图见本包 README；无独立 `patches/` 目录。

## Trigger / knobs / forbidden

1. **Trigger：** `ANOMALY_TRIGGER S11 mla_rope_pad`（query/kv），在 pad-tail 生效时打出。
2. **Allowed knobs：** MLA 模型；concurrent 变长 prefill；util / max-len / seqs；不开 APC；表已是 actual-sized 时再合成 pad 行。
3. **Forbidden：** 强制 NaN / token fill。

## 模型

`DeepSeek-V2-Lite`（MLA，已验证可跑）。

## Latest result

**PASS** `138 / 39 / 60`（`token_repeat`）——run `T190840` @ 160 `4,5`，DeepSeek-V2-Lite bf16。

## Expected detector

`token_repeat` 和 / 或 `logits_finite`。

## Origin-faithful protocol

三层率与 origin-faithful 约束以本包正文与私有 PRINCIPLES 为准。全文细节在本仓之外的历史记录里。
