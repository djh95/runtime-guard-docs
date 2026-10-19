# S43 · Embed ×100（PASS）

**现象：** 换行塌缩 / `token_repeat`。

**课：** Embed 幅度错 → 复读类可检。对照 **S45 GAP**（同 sampler/embed 族）。

**内部证据**（需 `runtime-guard-test`）：  
`tests/build-anomaly-env/fail-evidence/S43/` · `docs/anomaly-skills-runs/S43-20261017.md`
