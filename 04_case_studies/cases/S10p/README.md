# S10′ · FullAttn recycle-zero（PASS）

公开自洽个案包（不依赖私有 test 即可读完）。短例：[examples/S10p_fullattn-recycle-zero.md](../../examples/S10p_fullattn-recycle-zero.md)

## External five-bar

| # | 栏 | 文件 | 一句话 |
|---|----|------|--------|
| 1 | 现象 | [01_phenomenon.md](./01_phenomenon.md) | 短语/复读/`xxxx` 塌缩；`token_repeat` 大量命中（dete… |
| 2 | 根因 | [02_origin.md](./02_origin.md) | origin=`both` |
| 3 | Guard | [03_guard_gap.md](./03_guard_gap.md) | PASS · 65 / 20 / 79 |
| 4 | 复现 | [04_repro.md](./04_repro.md) | 按本包 + FE evidence 对齐 |
| 5 | 课 | [05_lesson.md](./05_lesson.md) | 带走的判断标准 |

证据：[evidence/](./evidence/)

## 钉（归档）

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
| 三层率 | **65 / 20 / 79** |
| Detector | token_repeat |
| Origin | `both` |
| Guard pin | G2 f2aefd068 |
| 模型 | Qwen3-8B（English concurrent load；见 status） |
| Scenario | `10_fullattn_recycle_zero` |
| Run | 10_fullattn_recycle_zero-20261016T181551 @ 160 cards 4,5 |
