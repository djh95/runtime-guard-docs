# S22 · Spec resample RNG/SALT（PASS）

**现象：** 接受率异常偏低；偶发 `token_repeat`。

**课：** 非文本主路径——分布性 detector `spec_acceptance`（#18657）。

**内部证据**（需 `runtime-guard-test`）：  
`tests/build-anomaly-env/fail-evidence/S22/` · `docs/anomaly-skills-runs/S22-20261017.md`
