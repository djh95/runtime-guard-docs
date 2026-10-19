# 3 · Guard 结果与 GAP

## 配置意图

归档当时启用 **`logits_finite`**（`item_sync`），触发后 `report` + `dump_kv`；`token_repeat` / `spec_acceptance` 关闭。

## 三层率（归档 `T165931` 顶层 status）

摘自 [evidence/status.json](./evidence/status.json) / [layers.json](./evidence/layers.json)：

| 层 | 数 | 含义 |
|----|---:|------|
| trigger | **136** | `ANOMALY_TRIGGER`（skip_zero / synth_block0） |
| precision | **25** | 当时脚本启发式；笔记几乎全是 `garbage_mixed_script:completion_*.json` |
| detect | **0** | 无 `report_*.json`；`logits_finite` **miss** |

`WHY_UNDETECTED`（[evidence/WHY_UNDETECTED.md](./evidence/WHY_UNDETECTED.md)）：garbage 有限 → `logits_finite` 只抓 NaN/Inf。

## GAP（产品课）

- **类：** 有限垃圾 / 跨请求相同 junk — **现网无专用 detector**。  
- **不是：**「Guard 没开」或「overlay 没打上」（trigger=136 说明路径在跑）。  
- **同族对照：** S10′ recycle → `token_repeat` **PASS**；S01 这条 → **漏检**。
