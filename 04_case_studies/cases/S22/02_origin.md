# 2 · 根因

拒绝校验与 residual resample 共用 RNG；无独立 salt → 恢复 token 偏置（#18657）。Overlay **只打 trigger 日志**，不造 NaN。≠ S05。

## Upstream / anchors

- https://github.com/vllm-project/vllm-ascend/pull/18657

## SPEC 摘录

见 [evidence/SPEC_excerpt.md](./evidence/SPEC_excerpt.md)（若有）。
