---
name: runtime-guard-detector-sweep
description: >-
  Enable shipped runtime_guard detectors together for intermittent NPU/vllm
  bugs so the hitting detector classifies the anomaly. Temporary triage only;
  turn unused detectors off after triage. Native dump_kv optional later.
---

# runtime_guard Detector Sweep

## When

- 偶发质量问题（复读 / 乱码 / NaN），复现贵，需要一次压测尽量分类  
- 未定类 → 临时多开 **已合入** detector（只 report，先不 dump）

> 多 detector 仅建议**临时排障**；开启后有 CPU 开销，排完关掉。见手册 [01](../../01_enable_and_start.md) / [03](../../03_detectors/README.md)。

## 已合入 detectors（#16849）

| Key | 抓什么 |
|-----|--------|
| `detector.token_repeat` | 局部复读 |
| `detector.logits_finite` | 采样前 NaN/Inf（#18644：短/错位 qsl 边界保护） |
| `detector.spec_acceptance` | Spec 接受率/长度异常（需 MTP；#18644：None accepted / 空 step 安全） |

**未合入（勿启用）**：`output_substring`、`token_logprob`、`slot_*`、`kv_state`。

## Procedure

1. 启动：`runtime_config_hot_reload=true` + 绝对路径 live JSON（启动后再改文件）。  
2. 热更（dump 先关）：

```jsonc
// 临时 sweep：只 report
{
  "dump": { "auto_max_times": 0, "manual_dump": false },
  "report": { "max_per_req": 1, "save_sensitive_info": true },
  "detector": {
    "token_repeat": { "enabled": true, "on_trigger": ["report"] },
    "logits_finite": { "enabled": true, "on_trigger": ["report"] },
    "spec_acceptance": { "enabled": true, "on_trigger": ["report"] }  // 仅 MTP 时
  }
}
```

3. Grep worker 日志确认 reload 成功（失败会**保留旧配置**）。  
4. 多轮复现（建议 ≥20，按复现率放大）。  
5. 汇总：

```bash
PYTHONPATH="$RG_TEST" python -m analysis.scripts.summarize_reports \
  --report-dir ./runtime/report --limit 50
```

## 决策

| 模式 | 动作 |
|------|------|
| ≥5 次同 detector | 类确认 → investigation 开 dump + ref |
| 稳定多 detector 同组合 | 复合类 → dump；命中次序是线索 |
| 各次命中不同 | 继续 sweep / 调阈值，不急切 dump |
| 有现象无命中 | 回 triage；或 `manual_dump` 抓单侧现场 |
| 全是误报 | `config-recommender` 收紧阈值 |

## 解读

| 命中 | 倾向 | 下一步 |
|------|------|--------|
| `logits_finite` | 数值炸 | dump + ref；KV 干净则偏后采样 |
| `token_repeat` | 输出退化 | dump + `locate_first_divergence` |
| `spec_acceptance` | draft/verify 或统计链路 | 对照实验；慎开高频 dump |

## Notes

- 热更开关是启动参数 `runtime_config_hot_reload`，**不是** JSON `reload_interval_seconds`。  
- 停检用 `report.max_per_req`，**不是** `stop_after_alert`。  
- Detector 滞后：命中 dump 是 post-bug 状态；首坏 token 靠 report ids + 对比脚本。  
- 达 `max_per_req` 后**仅当前 req** 停检，其它请求不受影响。

## Related

- `runtime-guard-investigation` / `runtime-guard-config-recommender` / `runtime-guard-analysis`
