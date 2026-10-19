# S48 · Residual negate（PASS）

**现象：** 全请求 bang 塌缩。

**课：** 残差极性错 → `!!!!` / `logits_finite`。≠ residual-drop 近邻。

**内部证据**（需 `runtime-guard-test`）：  
`tests/build-anomaly-env/fail-evidence/S48/` · `docs/anomaly-skills-runs/S48-20261017.md`
