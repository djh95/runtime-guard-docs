# S26 · RMSNorm fp32 weight-mul（PASS）

**现象：** digit/复读；`token_repeat`。

**课：** PR-rooted soft-inv 样板（#42379）。C 矩阵 ones/zeros 变体不进 docs。

**内部证据**（需 `runtime-guard-test`）：  
`tests/build-anomaly-env/fail-evidence/S26/` · `docs/anomaly-skills-runs/S26-20261017.md`
