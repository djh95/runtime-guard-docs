# S25 · RoPE 第二半写丢（PASS）

**现象：** digit / `1.1.1…` 复读；`token_repeat`。

**课：** PR-rooted RoPE soft-inv（#7082）。≠ **S11** pad-tail。

**内部证据**（需 `runtime-guard-test`）：  
`tests/build-anomaly-env/fail-evidence/S25/` · `docs/anomaly-skills-runs/S25-20261017.md`
