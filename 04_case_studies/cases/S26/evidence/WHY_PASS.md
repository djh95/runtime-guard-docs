# S26 PASS — RMSNorm fp32 weight-mul

- Origin：soft-inverse [vLLM#42379](https://github.com/vllm-project/vllm/pull/42379)。
- Overlay：`AscendRMSNorm.forward_oot` 走 fp32-mul 再 cast。
- 现行三层：**354 / 16 / 48**（`token_repeat`；detect=48 精确）。
- 配方与 S25 相同：河名句 ×48 并发；threshold=8；temp=0。
- 首轮盲跑「FAIL detect=0」同属错配方，不是检测器漏检 / 特征佯差。
