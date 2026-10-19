# S50 · SwiGLU gate/up half-swap（PASS）

**现象：** identical `!!!!`；`logits_finite`×48。

**课：** 有限非数 / bang 塌缩可被 `logits_finite` 抓住 — 对照 S01/S07 有限但非 Inf 的汤。

**完整个案（公开自洽）：** [cases/S50/](../cases/S50/) — external five-bar + evidence。
