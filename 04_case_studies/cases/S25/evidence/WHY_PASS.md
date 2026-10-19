# S25 PASS — rope second-half write drop

- Origin: soft-inverse [ascend#7082](https://github.com/vllm-project/vllm-ascend/pull/7082) (missing Triton second-half store).
- Overlay: after `npu_rotary_embedding`, restore unrotated `[..., rd/2:rd]`.
- Run: `25_rope_siso_half_drop-20261017T115523` @ 160 cards `4,5`, Qwen3-8B.
- Layers: **462 / 15 / 48** (`token_repeat`).
- ≠ S11 (pad length).
