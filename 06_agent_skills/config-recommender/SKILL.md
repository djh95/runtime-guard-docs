---
name: runtime-guard-config-recommender
description: >-
  Recommend runtime_config parameters from observed bug phenomena: which
  shipped detectors, thresholds, auto_max_times, auto_cooldown_seconds,
  manual_dump, on_trigger (report + dump_kv), report.max_per_req. Native
  dump_kv only; no msprobe. Align with current product schema.
---

# runtime_guard Config Recommender

人读参数见上游 [runtime_config.md](https://github.com/vllm-project/vllm-ascend/blob/main/docs/source/user_guide/configuration/runtime_config.md) 与手册 [01](../../01_enable_and_start.md) / [03](../../03_detectors/README.md)。

## Step 1 — 现象分类

走 `runtime-guard-investigation` triage；不适合 Guard 则停。

## Step 2 — 已合入 detector 推荐

| 现象类 | Detector | 关键参数 | 备注 |
|--------|----------|----------|------|
| 复读 / 卡词 | `token_repeat` | `window:32`, `repeat_sum_threshold:64`, `min_tokens:32`, `consecutive_hits:1` | 最轻；热更改 `window` 会清空 per-req 状态 |
| NaN/Inf / 数值炸 | `logits_finite` | `item_sync:false`（默认）；要 grammar 前精确 kind 才 `true`（D2H 更贵） | #18644 qsl 边界 |
| Spec 接受异常 | `spec_acceptance` | `window:10`, `low_threshold:0.3`, `high_threshold:0.96`, … | 仅 MTP；#18644 None/空 step |
| 未定类 | 三键临时 sweep | 见 `detector-sweep` | **勿**开未合入键 |
| KV 可疑无 detector | — | `manual_dump` / `dump_kv` + ref | 无 slot detector |

**勿推荐**：`output_substring`、`token_logprob`、`slot_*`、`kv_state`。

每 detector：`on_trigger` 默认含 `report`；抓现场加 `"dump_kv"`。

## Step 3 — `auto_max_times`（复现率）

`auto_max_times ≈ N_expected_repros × (1/repro_rate) × 1.5`  
例：要 3 次现场、复现率 20% → `3×5×1.5 ≈ 25`。

## Step 4 — cooldown

默认 `auto_cooldown_seconds: 300`。复现率高可 60–120；低则保持或加大。

## Step 4b — 盘预算（与 Step 3 取小）

```text
auto_max_times ≤ (磁盘剩余 × 0.7) / per_req_size
```

`per_req_size` = 单请求 KV 快照预估（`du -sh .../wave_N/`）。多 rank 各写一份时放大分母。

## Step 5 — 停检语义

用 **`report.max_per_req`**（默认 1）：写满后**该 req** 停检。  
**没有**产品级 `stop_after_alert` 字段。

| 场景 | `max_per_req` |
|------|---------------|
| 抓一次现场够用 | `1` |
| 想看同 req 多次命中模式 | `>1`（注意配额与盘） |

## Step 6 — 推荐配置骨架

启动：`--additional-config` 含 `runtime_config_hot_reload: true`（启动后再改 JSON）。

**启服基线（dump 关）：**

```jsonc
{
  "dump": { "auto_max_times": 0, "manual_dump": false },
  "report": {
    "max_per_req": 1,
    "save_sensitive_info": true
  },
  "detector": {
    "token_repeat": {
      "enabled": true,
      "on_trigger": ["report"],
      "window": 32,
      "repeat_sum_threshold": 64
    }
  }
}
```

**压测抓 dump（热更）：**

```jsonc
// 仅临时排障，排完关掉 dump / 多余 detector
{
  "dump": {
    "auto_max_times": 3,
    "auto_cooldown_seconds": 300,
    "manual_dump": false
  },
  "detector": {
    "token_repeat": {
      "enabled": true,
      "on_trigger": ["report", "dump_kv"]
    }
  }
}
```

### Schema 要点

- 无 `dump.enabled`；活跃 = `auto_max_times>0` 或 manual 水位。  
- `auto_max_times>0` 与 active `manual_dump` **互斥**。  
- JSONC 合法；未知 detector key → reload **拒绝并保留旧配置**。  
- 热更开关不在 JSON；改同步拓扑需重启。

## Step 7 — 拓扑

- Report：last-PP **TP0**；dump：last-PP×全部 TP。  
- 同 EngineCore 各 TP 必须读同一 live JSON。  
- 默认全关 → static idle（几乎无开销）；开 detector/dump/热更才有额外 CPU。

## Related

- `runtime-guard-detector-sweep` / `runtime-guard-investigation` / `runtime-guard-analysis` / `runtime-guard-ref-kv-dump`
