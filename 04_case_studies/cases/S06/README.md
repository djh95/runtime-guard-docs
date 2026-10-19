# S06 · MoE routing bias / topk→0（PASS · 唯一公开 MoE）

公开自洽个案包（不依赖私有 test 即可读完）。短例：[examples/S06_moe-topk-zero.md](../../examples/S06_moe-topk-zero.md)

## External five-bar

| # | 栏 | 文件 | 一句话 |
|---|----|------|--------|
| 1 | 现象 | [01_phenomenon.md](./01_phenomenon.md) | MoE 路由偏置/mask 错误 → 错专家；归档有 `token_repeat… |
| 2 | 根因 | [02_origin.md](./02_origin.md) | origin=`both` |
| 3 | Guard | [03_guard_gap.md](./03_guard_gap.md) | PASS · 70 / 1 / report×1（status.layers.detect_reports=0 与 archived report 不一致 — 见正文） |
| 4 | 复现 | [04_repro.md](./04_repro.md) | 按本包 + FE evidence 对齐 |
| 5 | 课 | [05_lesson.md](./05_lesson.md) | 带走的判断标准 |

证据：[evidence/](./evidence/)

## 钉（归档）

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
| 三层率 | **70 / 1 / report×1（status.layers.detect_reports=0 与 archived report 不一致 — 见正文）** |
| Detector | token_repeat |
| Origin | `both` |
| Guard pin | G2 f2aefd068 |
| 模型 | DeepSeek-V2-Lite |
| Scenario | `06_moe_routing_bias` |
| Run | 06_moe_routing_bias-20261016T081459 @ 162 cards 0,1 |
