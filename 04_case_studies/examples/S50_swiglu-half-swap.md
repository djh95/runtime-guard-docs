# S50 · SwiGLU gate/up half-swap（PASS）

**现象：** 全请求 `!!!!…`；非有限 logits。

**课：** SwiGLU 算子 L2；常走 `logits_finite`。该 type 公开只留 1 个。

**内部证据**（需 `runtime-guard-test`）：  
`tests/build-anomaly-env/fail-evidence/S50/` · `docs/anomaly-skills-runs/S50-20261017.md`
