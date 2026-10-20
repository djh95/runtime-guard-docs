# S47 — K/V swap before attention

| 字段 | 值 |
|------|-----|
| **ID** | S47 |
| **Origin** | `both`（constructed swapped-KV） |
| **Priority** | P0 |
| **repro_mode** | `origin_tuned` |
| **difficulty** | `easy` |

## Origin

在 `reshape_and_cache` / FA 前 swap `key, value`。对正确 KV 赋值做 soft-inverse。不等于 S34 / S35 / S41。

## Overlay

见本包 patches / 生成脚本（历史记录名 `47_kv_swap`）。

## Trigger / knobs / forbidden

1. **Trigger：** `ANOMALY_TRIGGER S47 kv_swap`
2. **Allowed：** Qwen3-8B；concurrency
3. **Forbidden：** force-NaN；token `fill_`

## Model

`Qwen3-8B`

## Expected detector

`token_repeat` / `logits_finite`

更细的历史记录不在本仓；本包以上表与归档证据为准。
