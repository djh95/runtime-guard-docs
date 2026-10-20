# S26 PASS — RMSNorm fp32 weight-mul

- Origin：soft-inverse [vLLM#42379](https://github.com/vllm-project/vllm/pull/42379)。
- Overlay：`AscendRMSNorm.forward_oot` 走 fp32-mul 再 cast。
- Run：`26_rmsnorm_fp32_mul-20261017T115830` @ 160 cards `6,7`，Qwen3-8B。
- 三层：**470 / 14 / 48**（`token_repeat`）。
