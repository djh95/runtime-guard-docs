# 3 · Guard 结果

**判定：PASS**

`status.json` 写 `detect_reports=0`，但同 FE 含 archived `reports/report_*.json` 且 `incident_type=token_repeat`、`result=PASS`。**以 PASS + 归档报告为准**；记 status 字段滞后。

| 层 | 归档 |
|----|------|
| trigger / precision / detect | **70 / 1 / report×1（status.layers.detect_reports=0 与 archived report 不一致 — 见正文）** |
| 期望 detector | token_repeat |

证据文件见 `evidence/`（WHY / layers / samples / overlay 摘录）。
