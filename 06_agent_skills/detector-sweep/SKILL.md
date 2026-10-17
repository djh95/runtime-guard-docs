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

手册：[01](https://github.com/djh95/runtime-guard-docs/blob/main/01_enable_and_start.md) · [03](https://github.com/djh95/runtime-guard-docs/blob/main/03_detectors/README.md) · 契约：[SKILLS_METADATA.md](./SKILLS_METADATA.md)

## When

偶发质量问题、类别未知 → 一次压测尽量让**已合入** detector 先分类（只 report）。

## 已合入（#16849）

| Key | 抓什么 |
|-----|--------|
| `token_repeat` | 局部复读 |
| `logits_finite` | 采样前 NaN/Inf |
| `spec_acceptance` | Spec 接受率/长度（**仅 MTP**；非 MTP 不要开） |

**勿启用：** `output_substring` / `token_logprob` / `slot_*` / `kv_state`。

**已知 sweep 盲区（仍跑 samples）：** 有限 mixed-script 垃圾、跨请求完全相同 completion（S01/S07 class）——三键可能全空 report；压测后用 `score_completion_samples` 判 precision，标 GAP，不要把「无 report」当成「无异常」。

**数值溢出 / softcap（S20 class）：** sweep 开齐 `token_repeat`+`logits_finite`；塌缩成 `!!!!`/token0 时以 `token_repeat` 命中为准，勿因 `logits_finite` 空报就结案。

**Spec / eagle3（S22 class）：** 非 MTP 勿开 `spec_acceptance`；有 draft 时必须开。低接受率 + 正常文本仍算 precision（分布性），交给 analysis 读 report，勿只盯 samples。

**权重/量化 always-on（S23/S24）：** sweep 开 `token_repeat`（+可选 `logits_finite`）。命中后 **不要** 承诺定位参数；与 S07 FAIL+GAP 区分（S24 已可 detect）。

**RoPE / RMSNorm soft-inv（S25/S26/S28）：** 同样开 `token_repeat`。命中后交 analysis 做 **L2 class-hint**（half-drop / fp32-mul / neox→interleaved）；勿与 S11 MLA pad 混谈。

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
