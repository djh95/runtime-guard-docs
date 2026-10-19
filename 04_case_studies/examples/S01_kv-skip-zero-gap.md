# S01 · KV skip-zero → 有限垃圾（GAP）

**现象：** 输出有限但仍乱码/混合脚本；`logits_finite` 与 `token_repeat` 都漏。

**课：** 有限垃圾是 detector 缺口（≠ NaN、≠ 复读窗）。同族对照：**S10′** 能检、本例漏检。

**内部证据**（需 `runtime-guard-test`）：  
`tests/build-anomaly-env/fail-evidence/S01/` · `docs/anomaly-skills-runs/S01-20261017.md`
