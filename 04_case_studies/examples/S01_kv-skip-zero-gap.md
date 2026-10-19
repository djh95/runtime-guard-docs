# S01 · KV skip-zero → 有限垃圾（GAP）

**现象：** 输出有限但仍可能乱码/混合脚本；`logits_finite` 与 `token_repeat` 都漏。

**课：** 有限垃圾是 detector 缺口（≠ NaN、≠ 复读窗）。同族对照：**S10′** 能检、本例漏检。

**完整个案（公开自洽）：** [cases/S01/](../cases/S01/) — 现象 / 根因 / Guard GAP / Then-vs-Now / 课（external five-bar）。
