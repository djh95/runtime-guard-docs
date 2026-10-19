# S01 · KV skip-zero → 有限垃圾（detector GAP）

公开、自洽的个案包（**不依赖**私有 `runtime-guard-test` 也能读完）。  
对照短例：[examples/S01_kv-skip-zero-gap.md](../../examples/S01_kv-skip-zero-gap.md) · 同族 PASS：[examples/S10p_fullattn-recycle-zero.md](../../examples/S10p_fullattn-recycle-zero.md)

## External five-bar

| # | 栏 | 文件 | 一句话 |
|---|----|------|--------|
| 1 | 现象 | [01_phenomenon.md](./01_phenomenon.md) | 有限输出仍「脏」；`logits_finite` 不响 |
| 2 | 根因 | [02_origin.md](./02_origin.md) | 新 KV block 未置零（hybrid/量化语义）；origin=`both` |
| 3 | Guard | [03_guard_gap.md](./03_guard_gap.md) | 期望 `logits_finite`；归档 **136 / 25 / 0**；GAP=有限垃圾 |
| 4 | 复现 | [04_repro_then_vs_now.md](./04_repro_then_vs_now.md) | Then 评分虚高 + dense synth 假触发；Now dense 0 bad 不矛盾 |
| 5 | 课 | [05_lesson.md](./05_lesson.md) | 有限垃圾 ≠ NaN；对照 S10′；需 garbled-text detector |

证据摘录（本包内）：[evidence/](./evidence/)

## 钉（归档当时）

| 项 | 值 |
|----|-----|
| Guard pin | G2 · `f2aefd068c4bd299d91cf0a1fdf642a3f327308f` |
| 模型 | Qwen3-8B · TP2 |
| 结果 | `FAIL`（repro_mode=`origin_tuned`） |
| 期望 detector | `logits_finite` |
| 上游锚 | [vLLM#43990](https://github.com/vllm-project/vllm/pull/43990) · [#47574](https://github.com/vllm-project/vllm/pull/47574) |
