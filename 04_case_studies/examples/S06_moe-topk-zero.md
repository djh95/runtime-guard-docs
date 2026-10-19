# S06 · MoE routing bias / topk→0（PASS · 唯一公开 MoE）

**现象：** MoE 路由偏置/mask 错误 → 错专家；归档有 `token_repeat` 报告 + repeat 样本文。

**课：** MoE 饱和类不在公开 keep 刷分；这一例只作路由模版。

**完整个案（公开自洽）：** [cases/S06/](../cases/S06/) — external five-bar + evidence。
