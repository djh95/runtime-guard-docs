# S48 · Residual negate（PASS）

**现象：** identical `!!!!`；`logits_finite`×48。

**课：** 极性错误 → bang / nonfinite 路径；与 residual-drop 区分。

**完整个案（公开自洽）：** [cases/S48/](../cases/S48/) — external five-bar + evidence。
