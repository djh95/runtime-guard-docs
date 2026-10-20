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

**FAIL+GAP** —— trigger 有；各不相同乱码；`detect=0`（**乱码检测漏检**）。不要当成 PASS，也不要用 amplifier-retune。证据见 `WHY_UNDETECTED.md` + samples。

## Overlay

见本包 patches / 生成脚本（历史配方名 `45_topk_bottom_keep`）。

## Trigger / knobs / forbidden

1. **Trigger：** `ANOMALY_TRIGGER S45 topk_bottom_keep`
2. **Allowed：** Qwen3-8B；`top_k`；concurrency；**temp=0.8**
3. **Forbidden：** force-NaN；token `fill_`；logits.zero_

## HOW_TO / 复现配方

```
overlay: gen_s45_overlay.py → 双树写入（Ascend platform.py + vllm sampler.py）
temperature: 0.8（勿用 0）
concurrency: 48
```

只打 Ascend B → 缺 sampler；temp=0 → 对不上。二次盲跑对齐后 **16 / 4 / 0** 漏检精确复现。

## Model

`Qwen3-8B`

## Evidence

本包 `WHY_FAIL.md` / `WHY_UNDETECTED.md` + `samples/`。现行三层：**16 / 4 / 0**。
