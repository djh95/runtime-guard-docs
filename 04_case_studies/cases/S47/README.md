# S47 · Attn K/V swap（PASS）

公开自洽个案包（不依赖私有 test 即可读完）。

## External five-bar

| # | 栏 | 文件 | 一句话 |
|---|----|------|--------|
| 1 | 现象 | [01_phenomenon.md](./01_phenomenon.md) | CJK/Trail 塌缩；`token_repeat`×48。… |
| 2 | 根因 | [02_origin.md](./02_origin.md) | origin=`both（constructed）` |
| 3 | Guard | [03_guard_gap.md](./03_guard_gap.md) | PASS · 58 / 37 / 48 |
| 4 | 复现 | [04_repro.md](./04_repro.md) | 按本包 + FE evidence 对齐 |
| 5 | 课 | [05_lesson.md](./05_lesson.md) | 带走的判断标准 |

证据：[evidence/](./evidence/)

## 钉（归档）

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
| 三层率 | **58 / 37 / 48** |
| Detector | token_repeat |
| Origin | `both（constructed）` |
| Guard pin | G2 f2aefd068 |
| 模型 | Qwen3-8B |
| Scenario | `47_kv_swap` |
| Run | 47_kv_swap-20261017T164919 @ 160 cards 10,11 |
