# S01 证据分组（trigger / precision / detect 都要留）

## A · Trigger（路径打中）

- 复判计数：[layers.json](./layers.json) / [status.json](./status.json) → `trigger_events=154`
- 文案摘录：[trigger_excerpt.txt](./trigger_excerpt.txt)
- Overlay 规模：[overlay_full.files.txt](./overlay_full.files.txt)、[overlay_full.wc.txt](./overlay_full.wc.txt)；早期残缺：[overlay_early_partial.stat.txt](./overlay_early_partial.stat.txt)

## B · Precision（异常输出？）

- 复判样本（prompt+completion）：[samples/](./samples/)
- 中文误报核对：[precision_cjk_audit.md](./precision_cjk_audit.md)
- 结论：可见样本**不是**乱码；旧 heuristic precision=25 / 复判虚报 25 → CJK 排除后 **0**

## C · Detect（Guard 是否报警）

- `detect_reports=0`；[report_emptiness.txt](./report_emptiness.txt)
- WHY：[WHY_UNDETECTED.md](./WHY_UNDETECTED.md)

三组一起读：有 trigger、无真实坏输出、detect 空 → **FAIL（复现未出现）**。不要把 CJK 误报当成乱码已复现，也不要写成 FAIL+GAP。
