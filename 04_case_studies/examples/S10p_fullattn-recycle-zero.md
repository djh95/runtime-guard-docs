# S10′ · FullAttn recycle-zero（PASS）

**现象：** 短语/复读/`xxxx` 塌缩；`token_repeat` 大量命中（detect 79 / 80 req）。

**课：** 同大类 KV 脏读：**S10′ 能检**（recycle），**S01 漏检**（skip-zero→有限垃圾）。

**完整个案（公开自洽）：** [cases/S10p/](../cases/S10p/) — external five-bar + evidence。
