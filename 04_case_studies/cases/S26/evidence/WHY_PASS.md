# S26 PASS — RMSNorm fp32 weight-mul

- Origin：soft-inverse [vLLM#42379](https://github.com/vllm-project/vllm/pull/42379)。
- Overlay：`AscendRMSNorm.forward_oot` 走 fp32-mul 再 cast。
- 现行三层：**354 / 16 / 48**（`token_repeat`；detect=48/48）。
- 复现技巧与 S25 相同：河名句 ×48 并发；threshold=8；temp=0。
- 勿用中文回声 / 串行 8 / 阈值 16。
