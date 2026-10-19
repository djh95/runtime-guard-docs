# 2 · 根因

FullAttention 不进 `needs_kv_cache_zeroing` 管线 → 回收 block partial-tail 脏 K/V（#39283/#43741）。与 **S01** 对照：S01=进 zeroer 后 skip；S10′=永不进 FullAttn zeroing。

## Upstream / anchors

- https://github.com/vllm-project/vllm/pull/39283
- https://github.com/vllm-project/vllm/pull/43741

## SPEC 摘录

见 [evidence/SPEC_excerpt.md](./evidence/SPEC_excerpt.md)（若有）。
