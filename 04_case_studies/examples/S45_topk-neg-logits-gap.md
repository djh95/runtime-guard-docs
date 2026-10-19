# S45 · top-k on `-logits` → unique garbage（GAP）

**现象：** 每请求不同乱码；`token_repeat` / `logits_finite` 双漏。

**课：** 第三种漏检形态（unique garbage）。对照 **S43 PASS**。

**内部证据**（需 `runtime-guard-test`）：  
`tests/build-anomaly-env/fail-evidence/S45/` · `docs/anomaly-skills-runs/S45-20261017.md`
