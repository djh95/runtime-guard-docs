# S10′ · FullAttn recycle-zero（PASS）

**现象：** 短语/复读塌缩；`token_repeat` 命中。

**课：** KV recycle 未清零可被检到。与 **S01 GAP** 对照：同大类，一边 PASS 一边漏。公开文件名 `S10p_`；FE 目录 `S10/`。

**内部证据**（需 `runtime-guard-test`）：  
`tests/build-anomaly-env/fail-evidence/S10/` · `docs/anomaly-skills-runs/batch-pass-wave-20261017.md`
