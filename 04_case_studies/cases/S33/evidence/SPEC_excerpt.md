# S33 — Incomplete final-logit softcap

| 字段 | 值 |
|------|-----|
| **ID** | S33 |
| **Origin** | `both`（constructed softcap class） |
| **Priority** | P0 |
| **repro_mode** | `origin_tuned` |
| **difficulty** | `easy` |

## Origin

Softcap / `final_logit_softcapping` 类（[vLLM#56579](https://github.com/vllm-project/vllm/pull/56579) 族；Gemma `final_logit_softcapping`）。对正确 softcap 做 soft-inverse：`÷cap + tanh`，但 **跳过 `*cap` rescale**。模型本身没有 softcap 时，boot 强制 cap=30。不等于 S20（V2 sampler 上不稳定的 exp/tanh Inf/Inf）。

## Overlay

见本包 patches / 生成脚本（历史配方名 `33_softcap_incomplete`）。

## Trigger / knobs / forbidden

1. **Trigger：** `ANOMALY_TRIGGER S33 softcap_incomplete`
2. **Allowed：** Qwen3-8B；concurrency
3. **Forbidden：** force-NaN；token `fill_`

## Model

`Qwen3-8B`（若偏好 softcap-native，也可考虑 Gemma4）

## Expected detector

`token_repeat`。归档 **PASS** 132/15/48。

更细的历史配方不在本仓；本包以上表与归档证据为准。
