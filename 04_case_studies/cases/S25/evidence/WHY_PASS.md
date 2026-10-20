# S25 PASS — RoPE second-half write drop

- Origin：soft-inverse [ascend#7082](https://github.com/vllm-project/vllm-ascend/pull/7082)（Triton 后半维缺 store）。
- Overlay：`npu_rotary_embedding` 之后，恢复未旋转的 `[..., rd/2:rd]`。
- 现行三层：**348 / 17 / 48**（`token_repeat`；detect=48/48）。
- 配方：`Name one famous river. One short English sentence. id={i}.` ×48 并发；threshold=8；temp=0。
- 勿用：中文回声 + 串行 8 + 阈值 16（错配方 → detect=0，不是漏检）。
- 不等于 S11（pad 长度）。
