# S22 — Spec residual resample RNG collide（无 SALT）

| 字段 | 值 |
|------|-----|
| **ID** | S22 |
| **Origin** | `ascend-only`（+ cousin [vLLM#61161](https://github.com/vllm-project/vllm/pull/61161)） |
| **Priority** | P0 |
| **KV?** | draft KV present（spec） |
| **Guard pin** | G2 `f2aefd068` |
| **repro_mode** | `origin_tuned` |
| **difficulty** | `easy`–`medium`（detect 可能偏分布 → FAIL+GAP 风险） |

## Origin 说明

Rejection verification 与 residual categorical resample 共用同一 RNG `(seed, position)`。没有独立 salt 时，拒绝后恢复出的 token 会 **偏置**（例如 one-hot draft 在 0、target `[0.5,0.25,0.25]` 时总恢复成 token 2）——[ascend#18657](https://github.com/vllm-project/vllm-ascend/pull/18657)。

**G2 pin 本身已缺 `RESAMPLE_NOISE_SALT`**（修复只在 main / 0.30.0 backport）。Overlay 只在 residual resample 入口加 trigger 日志，**不**发明 NaN / `fill_`。与 S05（NaN argmax / uniform 0）、S20（softcap overflow）区分。

## 上游锚点

- https://github.com/vllm-project/vllm-ascend/pull/18657
- https://github.com/vllm-project/vllm/pull/61161

## Overlay

见本包 [`overlay.patch`](./overlay.patch) 与 `gen_s22_overlay.py`（锚点替换，自适应 CRLF/LF）。无独立 `patches/` 目录。

## Trigger / knobs / forbidden

1. **Trigger：** `ANOMALY_TRIGGER S22 spec_resample_rng_collide`
2. **Allowed knobs：** eagle3 + `temperature>0`；`num_speculative_tokens`；concurrency；seeds
3. **Forbidden：** 强制 NaN；token `fill_`；在未写明 pin 状态的前提下先发明 SALT 再拿掉

## 模型

`Qwen3-8B` + eagle3（G2 上已验证可 boot）。

## Expected detector

主：`spec_acceptance`；兼 `token_repeat`。

## HOW_TO / 复现技巧

```
model: Qwen3-8B + eagle3
temperature: 0.8
num_speculative_tokens: 3
concurrency: 48
eager / util=0.40
overlay: gen_s22_overlay.py（锚点替换；自适应 CRLF/LF）
```

静态 `git apply` 遇 **CRLF 源 + LF patch** 会对不上 → 用锚点脚本或 `apply_anomaly_overlay.sh --ignore-whitespace`。

## Origin-faithful protocol

现行三层：**126 / 0 / 47**。
