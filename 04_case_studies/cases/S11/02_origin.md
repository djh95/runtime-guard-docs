# 2 · 根因

逆修复 ascend#18798：graph-pad 下 cos/sin **pad-tail** 喂 query RoPE（KV slice 在本 pin 保持正确）。≠ recycle（S10′）。禁止 NaN/fill。

## Upstream / anchors

- https://github.com/vllm-project/vllm-ascend/pull/18798

## SPEC 摘录

见 [evidence/SPEC_excerpt.md](./evidence/SPEC_excerpt.md)（若有）。
