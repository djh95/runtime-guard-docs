---
name: runtime-guard-detector-sweep
description: >-
  Emit a minimal temporary runtime_config that enables all shipped
  runtime_guard detectors with on_trigger report only and dump off, for
  unclassified intermittent bugs. No thresholds, no dump_kv, no offline
  report parsing. After a hit, hand off to config-recommender.
---

# runtime_guard Detector Sweep（极简筛查）

**类型：原子 · 在线配置。** 只产出临时 sweep 模板；不做读盘、不做阈值调优。

手册：[01](../../01_enable_and_start.md) · [03](../../03_detectors/README.md) · 契约：[SKILLS_METADATA.md](../SKILLS_METADATA.md)

## When

偶发质量问题、类别未知 → 一次压测尽量让**已合入** detector 先分类（只 report）。

## 已合入（#16849）

| Key | 抓什么 |
|-----|--------|
| `token_repeat` | 局部复读 |
| `logits_finite` | 采样前 NaN/Inf |
| `spec_acceptance` | Spec 接受率/长度（**仅 MTP**；非 MTP 不要开） |

**勿启用：** `output_substring` / `token_logprob` / `slot_*` / `kv_state`。

## 输出模板（可热更）

启动须已开 `runtime_config_hot_reload=true`（见 01）。Grep 确认 reload；失败会保留旧配置。

```jsonc
// 临时 sweep：只 report，禁止业务长期运行
{
  "dump": { "auto_max_times": 0, "manual_dump": false },
  "report": { "max_per_req": 1, "save_sensitive_info": true },
  "detector": {
    "token_repeat": { "enabled": true, "on_trigger": ["report"] },
    "logits_finite": { "enabled": true, "on_trigger": ["report"] },
    "spec_acceptance": { "enabled": true, "on_trigger": ["report"] }  // 仅 MTP
  }
}
```

允许的开关级字段：`enabled` / `on_trigger:["report"]` / dump 全关 / `max_per_req` / `save_sensitive_info`。

## forbidden

- window、阈值、`ignore_token_ids`、`auto_max_times>0`、cooldown、`dump_kv`  
- 解析本地 report/dump（→ `runtime-guard-analysis`）  
- 当作正式长期业务配置

## 后续

命中后 → `runtime-guard-config-recommender` 出正式阈值与（按需）dump 配额。  
读报告目录 → `analysis`。端到端编排 → `investigation`。

## Related

`config-recommender` · `analysis` · `investigation`
