# S22 · Spec resample 无 SALT（PASS · spec_acceptance）

**现象：** acceptance_rate 异常偏低（约 0–0.27，mean ~0.07–0.09）；`spec_acceptance`×45 + `token_repeat`×3。

**课：** Spec 路径要用对 detector；勿用有限/复读阈值解释 acceptance 塌缩。

**完整个案（公开自洽）：** [cases/S22/](../cases/S22/) — external five-bar + evidence。
