# S07 · W8A8 scale collapse → 有限垃圾（GAP）

公开自洽个案包（不依赖私有 test 即可读完）。

## External five-bar

| # | 栏 | 文件 | 一句话 |
|---|----|------|--------|
| 1 | 现象 | [01_phenomenon.md](./01_phenomenon.md) | **真·混合脚本汤**且跨请求 identical×48（归档 `sample_… |
| 2 | 根因 | [02_origin.md](./02_origin.md) | origin=`both` |
| 3 | Guard | [03_guard_gap.md](./03_guard_gap.md) | FAIL+GAP · 2624 / 1(identical×48) / 0 |
| 4 | 复现 | [04_repro.md](./04_repro.md) | 按本包 + FE evidence 对齐 |
| 5 | 课 | [05_lesson.md](./05_lesson.md) | 带走的判断标准 |

证据：[evidence/](./evidence/)

## 钉（归档）

| 项 | 值 |
|----|-----|
| 结果 | **FAIL+GAP** |
| 三层率 | **2624 / 1(identical×48) / 0** |
| Detector | logits_finite（miss） |
| Origin | `both` |
| Guard pin | G2 f2aefd068 |
| 模型 | Qwen3-8B-W8A8 TP2 |
| Scenario | `07_quant_scale_collapse` |
| Run | 07_quant_scale_collapse-20261016T084241 |
