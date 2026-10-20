# S25 PASS — RoPE second-half write drop

- Origin：soft-inverse [ascend#7082](https://github.com/vllm-project/vllm-ascend/pull/7082)（Triton 后半维缺 store）。
- Overlay：`npu_rotary_embedding` 之后，恢复未旋转的 `[..., rd/2:rd]`。
- 现行三层：**348 / 17 / 48**（`token_repeat`；detect=48 精确）。
- 配方：`Name one famous river. One short English sentence. id={i}.` ×48 并发；threshold=8；temp=0。
- 首轮盲跑「FAIL detect=0」是**错配方**（中文回声 + 串行 8 + 阈值 16），不是检测器漏检 / 特征佯差。
- 不等于 S11（pad 长度）。
