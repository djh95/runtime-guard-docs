# S25 PASS — RoPE second-half write drop

- Origin：soft-inverse [ascend#7082](https://github.com/vllm-project/vllm-ascend/pull/7082)（Triton 后半维缺 store）。
- Overlay：`npu_rotary_embedding` 之后，恢复未旋转的 `[..., rd/2:rd]`。
- Run：`25_rope_siso_half_drop-20261017T115523` @ 160 cards `4,5`，Qwen3-8B。
- 三层：**462 / 15 / 48**（`token_repeat`）。
- 不等于 S11（pad 长度）。
