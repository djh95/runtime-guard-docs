# 2 · 根因（origin-faithful）

| 字段 | 值 |
|------|-----|
| **Origin** | `both`（vLLM 与 Ascend 同失败模式） |
| **语义** | 新分配 KV block **未置零** → 读脏页 |
| **典型栈** | **hybrid / 量化 KV**（非「任意 dense bf16」） |

## 上游

- [vLLM#43990](https://github.com/vllm-project/vllm/pull/43990)  
- [vLLM#47574](https://github.com/vllm-project/vllm/pull/47574)  
- Ascend 对照：`_zero_block_ids` / `AscendKVBlockZeroer`（V1/V2）

## Overlay 意图（教学摘要）

完整 anomaly overlay（约 **251 行 / 5 文件**）会：

1. 强制 `needs_kv_cache_zeroing`；  
2. wrap / skip `KVBlockZeroer.zero_block_ids`（打 `ANOMALY_TRIGGER … skip_zero_upstream`）；  
3. 对 dense 路径 **synth_block0**——注释本意是「dense 可能从不跟踪新 block，合成 block0 让 skip-zero 消费者仍跑」。

**重要：** synth_block0 抬的是 **trigger 日志**，不等于「读到了脏 KV 汤」。早期残缺 overlay（[evidence/overlay_early_partial.stat.txt](./evidence/overlay_early_partial.stat.txt)：2 文件 / +18 行）连路径都不完整 → 无 anomaly。

文件清单见 [evidence/overlay_full.files.txt](./evidence/overlay_full.files.txt)。
