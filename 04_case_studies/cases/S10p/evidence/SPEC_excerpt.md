# S10′ — FullAttention recycled KV blocks not zeroed

| 字段 | 值 |
|------|-----|
| **ID** | S10′ (folder `10_fullattn_recycle_zero`; replaces softcap S10) |
| **Origin** | `both` |
| **Priority** | P0 |
| **KV?** | **是** |
| **Guard pin** | G2 `f2aefd068` |
| **repro_mode** | `origin_tuned` |
| **difficulty** | `easy` |

## Origin 说明

上游曾把 `needs_kv_cache_zeroing` 仅开给 Mamba（后亦含 mixed-precision），**FullAttention** 不进 zeroing 管线 → 回收 block 的 partial-tail 残留脏 K/V → 非确定 / 垃圾输出（[vLLM#39283](https://github.com/vllm-project/vllm/pull/39283)、[#43741](https://github.com/vllm-project/vllm/pull/43741)；issue [#39146](https://github.com/vllm-project/vllm/issues/39146)）。Ascend 共用 `KVCacheConfig.needs_kv_cache_zeroing` + `new_block_ids_to_zero` → **`both`**。

与 **S01** 区别：S01 = 强制进入 zeroer 后 **skip zero**（#43990/#47574）；S10′ = **永不进入** FullAttention zeroing（#39283 门控缺失）。

## Upstream anchors

- https://github.com/vllm-project/vllm/pull/39283
- https://github.com/vllm-project/vllm/pull/43741
- https://github.com/vllm-project/vllm/issues/39146

## Overlay

见 [`patches/README.md`](./patches/README.md)：`needs_kv_cache_zeroing → False` + `BlockPool.get_new_blocks` 上 `ANOMALY_TRIGGER`（recycle without zero）。禁止 NaN / token-fill。

## Trigger / knobs / forbidden

1. **Trigger predicate:** Free-pool handout while FullAttention zeroing gate is OFF (`ANOMALY_TRIGGER S10 fullattn_recycle_zero`).
2. **Allowed knobs:** `gpu_memory_utilization`, `max-model-len`, `max-num-seqs`, no APC, many short reqs @ `temperature=0`, concurrency/churn.
3. **Forbidden:** force NaN / `fill_` amplifiers.

## ≤5min 复现配方

1. Overlay 生效；TP2；`--no-enable-prefix-caching`；util≈0.40；高 `max-num-seqs`。
2. 冷启动后突发多请求，促使 block recycle。
3. 三层：trigger / precision（garbage 或 divergence）/ detect。

## 模型

`Qwen3-8B` TP2（dense FullAttention）。

## Expected detector

…（全文在私有 test 仓历史；本包以上表+FE 为准）
