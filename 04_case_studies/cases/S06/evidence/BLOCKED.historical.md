# S06 — permanent BLOCKED (not FAIL)

## Root cause
Cannot get a **healthy MoE boot** on this Guard pin / CANN stack with available free NPU HBM:

1. **DeepSeek-V2-Lite / Moonlight-16B-A3B**: boot dies with  
   `RuntimeError: aclnnAddRmsNormBias ... not in libopapi.so`  
   (CANN/opapi gap on this image).
2. **Qwen3-30B-A3B** TP2: process **OOM-killed** during load (`Killed` in runner) when free HBM on idle NPUs is insufficient for MoE weights + KV.

## Classification
**setup/BLOCKED** — overlay never exercised under a live server. Not a detector FAIL.

## Attempts (2026-10-16)
- DeepSeek-V2-Lite TP2: aclnnAddRmsNormBias
- Moonlight-16B-A3B TP2: same ACL error
- Qwen3-30B-A3B TP2 util 0.75: OOM kill mid-boot
