# S06 · MoE topk→0（PASS）

**现象：** 复读塌缩；`token_repeat`。

**课：** 公开唯一 MoE 模版（路由 L2）；近邻饱和案不进 docs。

**内部证据**（需 `runtime-guard-test`）：  
`tests/build-anomaly-env/fail-evidence/S06/` · `docs/anomaly-skills-runs/S06-20261017.md`
