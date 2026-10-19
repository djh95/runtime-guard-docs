# S47 · Attn Q/K/V·out（PASS）

**现象：** 复读 / `token_repeat`。

**课：** Attn 算子族 L2 代表；C 矩阵 ones/zeros 变体不进 docs。

**内部证据**（需 `runtime-guard-test`）：  
`tests/build-anomaly-env/fail-evidence/S47/` · `docs/anomaly-skills-runs/S47-20261017.md`
