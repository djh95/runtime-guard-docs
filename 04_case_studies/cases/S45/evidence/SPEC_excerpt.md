# S45 — Top-k/top-p direction flip（bottom nucleus）

| 字段 | 值 |
|------|-----|
| **ID** | S45 |
| **Origin** | `both`（constructed wrong-topk-direction） |
| **Priority** | P0 |
| **repro_mode** | `origin_tuned` |
| **difficulty** | **FAIL**（detect miss） |

## Origin

把 top-k / top-p 作用在 `-logits` 上再取反——保留最低-k / 倒置 nucleus。对比较方向做 soft-inverse。**不是**放大器。

## Status

**FAIL+GAP** —— trigger 有；precision 是 unique garbage；`detect=0`（没有 local re-reads / nonfinite）。已 park；不要当成 PASS，也不要用 amplifier-retune。证据见 `WHY_UNDETECTED.md` + ≥3 个 samples。

## Overlay

见本包 patches / 生成脚本（历史配方名 `45_topk_bottom_keep`）。

## Trigger / knobs / forbidden

1. **Trigger：** `ANOMALY_TRIGGER S45 topk_bottom_keep`
2. **Allowed：** Qwen3-8B；`top_k`；concurrency
3. **Forbidden：** force-NaN；token `fill_`；logits.zero_

## Model

`Qwen3-8B`

## Evidence

本包 `WHY_FAIL.md` / `WHY_UNDETECTED.md` + `samples/`。

更细的历史配方不在本仓；本包以上表与归档证据为准。
