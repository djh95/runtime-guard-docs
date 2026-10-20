# S43 — Embedding scale blowup（×100）

| 字段 | 值 |
|------|-----|
| **ID** | S43 |
| **Origin** | `both`（constructed wrong-embed-scale） |
| **Priority** | P0 |
| **repro_mode** | `origin_tuned` |
| **difficulty** | `easy` |

## Origin

Embedding lookup 之后 `mul_(100)`。对正确 embed magnitude 做 soft-inverse。不等于 S23 weight-zero，也不等于 S41 attn-out。

## Overlay

见本包 patches / 生成脚本（历史配方名 `43_embed_scale_blowup`）。

## Trigger / knobs / forbidden

1. **Trigger：** `ANOMALY_TRIGGER S43 embed_scale_blowup`
2. **Allowed：** Qwen3-8B；concurrency
3. **Forbidden：** force-NaN；token `fill_`

## Model

`Qwen3-8B`

## Expected detector

`logits_finite` / `token_repeat`

更细的历史配方不在本仓；本包以上表与归档证据为准。
