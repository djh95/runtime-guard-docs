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

见 [`patches/README.md`](./patches/README.md)。

## Trigger / knobs / forbidden

1. **Trigger：** `ANOMALY_TRIGGER S22 spec_resample_rng_collide`
2. **Allowed knobs：** eagle3 + `temperature>0`；`num_speculative_tokens`；concurrency；seeds
3. **Forbidden：** 强制 NaN；token `fill_`；在未写明 pin 状态的前提下先发明 SALT 再拿掉

## 模型

`Qwen3-8B` + eagle3（G2 上已验证可 boot）。

## Expected detector

偏置足够强时：`token_repeat` / `spec_acceptance`；否则可能 **FAIL+GAP**，需要 recovered-token histogram + samples（分布性）。

## Origin-faithful protocol

更细的历史配方不在本仓；本包以上表与归档证据为准。
