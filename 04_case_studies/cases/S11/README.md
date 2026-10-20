# S11 · MLA RoPE pad-tail（PASS）

公开自洽个案包（不依赖私有 test 即可读完）。

## External five-bar

| # | 栏 | 文件 | 一句话 |
|---|----|------|--------|
| 1 | 现象 | [01_phenomenon.md](./01_phenomenon.md) | digit/collapse junk（如 `1010…`）；`token_re… |
| 2 | 根因 | [02_origin.md](./02_origin.md) | origin=`ascend-only` |
| 3 | Guard | [03_guard_gap.md](./03_guard_gap.md) | PASS · 138 / 39 / 60 |
| 4 | 复现 | [04_repro.md](./04_repro.md) | 按本包 + FE evidence 对齐 |
| 5 | 课 | [05_lesson.md](./05_lesson.md) | 带走的判断标准 |

证据：[evidence/](./evidence/)

## 钉（归档）

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
| 三层率 | **138 / 39 / 60** |
| Detector | token_repeat |
| Origin | `ascend-only` |
| Guard pin | G2 f2aefd068 |
| 模型 | DeepSeek-V2-Lite MLA bf16 |
| Scenario | `11_mla_rope_pad` |
| Run | 11_mla_rope_pad-20261016T190840 @ 160 cards 4,5 |
