---
name: runtime-guard-config-recommender
description: >-
  Sole source of full runtime_guard runtime_config for triage: choose shipped
  detectors, thresholds, on_trigger, auto_max_times, cooldown, max_per_req;
  modes troubleshoot vs business_default (all off). No offline report/dump
  parsing and no end-to-end orchestration. Native dump_kv only; no msprobe.
---

# runtime_guard Config Recommender（正式配置唯一来源）

**类型：原子 · 在线配置。** 排障 JSON / 业务默认全关 **只从此 skill 产出**（sweep 仅极简临时模板）。

人读：[runtime_config.md](https://github.com/vllm-project/vllm-ascend/blob/main/docs/source/user_guide/configuration/runtime_config.md) · 手册 [01](https://github.com/djh95/runtime-guard-docs/blob/main/01_enable_and_start.md) / [03](https://github.com/djh95/runtime-guard-docs/blob/main/03_detectors/README.md)  
契约：[SKILLS_METADATA.md](./SKILLS_METADATA.md)

## Step 1 — 模式

| `mode` | 含义 |
|--------|------|
| `troubleshoot` | 开目标 detector；按需 `dump_kv` + 配额 |
| `business_default` | detector 全关、dump 关（`is_fully_off` 冷路径） |

未定类先走 `detector-sweep`，不要在本 skill 开「全 detector + 调优阈值」混模板。  
不适合 Guard 的现象（Hang/OOM/…）→ 停，见 investigation triage。

## Step 2 — 已合入 detector（troubleshoot）

| 现象类 | Detector | 关键参数 | 备注 |
|--------|----------|----------|------|
| 复读 / 卡词 / digit·`***`·ctx echo / `!!!!` token0 塌缩 / 句级短语复读 | `token_repeat` | `window:32`, `repeat_sum_threshold:64`, `min_tokens:32`, `consecutive_hits:1` | MoE / KV recycle / MLA pad / **S20 softcap** / **S25–S28 RoPE·RMSNorm soft-inv**；热更改 `window` 清 per-req 状态 |
| NaN/Inf / 数值炸（logits 仍 non-finite） | `logits_finite` | `item_sync:false`（默认）；要 grammar 前精确 kind 才 `true` | #18644 qsl 边界；**抓不到有限垃圾**；溢出若已塌成 token0 可能 **miss** → 仍靠 `token_repeat` |
| Softcap / 不稳定 exp-softmax 溢出嫌疑 | **两者都开** | `token_repeat` + `logits_finite`，只 report 先 | 低 temperature 放大；勿只信 `logits_finite` |
| RoPE half-drop / style flip / RMSNorm dtype（S25/S26/S28） | `token_repeat`（主） | 可兼开 `logits_finite` 对照 | **L2 class-hint**；≠ S11 pad；勿输出「定位到 rotary/store 行」 |
| 权重 / 量化 always-on 故障（S23/S24） | `token_repeat`（主） | 可兼开 `logits_finite` 对照 | **detect-only**：报告即交付；勿输出「定位到 layer/scale」；S24≠S07 GAP |
| Spec 接受异常 / residual resample 偏置 | `spec_acceptance` | `window:5–10`, `low_threshold:0.3–0.5`, `high_threshold:0.96–0.99`, … | **仅 MTP/eagle3**；S22 类（无 `RESAMPLE_NOISE_SALT`）以低 acceptance_rate 命中；可兼开 `token_repeat` |
| KV 可疑无 detector | — | `manual_dump` / `dump_kv` + 后续 ref | 无 slot detector |
| mixed-script / 跨请求全同垃圾 | **无已合入** | 仍可临时开 `token_repeat`+`logits_finite` 对照 | **已知 GAP**（S01/S07）；归档 samples，勿调阈值「硬凑」PASS |

**勿推荐：** `output_substring` / `token_logprob` / `slot_*` / `kv_state`。  
`on_trigger`：默认 `["report"]`；抓现场加 `"dump_kv"`。  
Anomaly 压测：优先 `token_repeat` + `save_sensitive_info:true`；预期有限垃圾场景在 recommender 输出里写明 **detect 可能为 0（GAP）**。

## Step 3 — 配额与停检

- `auto_max_times ≈ N_expected_repros × (1/repro_rate) × 1.5`  
- `auto_cooldown_seconds` 默认 300；高频复现可 60–120  
- 盘预算：`auto_max_times ≤ (磁盘剩余 × 0.7) / per_req_size`（与上式取小）  
- 停检用 **`report.max_per_req`**（无 `stop_after_alert`）

## Step 4 — 骨架

启动：`runtime_config_hot_reload=true`（不在 JSON 内）。

**troubleshoot · 先只 report：**

```jsonc
{
  "dump": { "auto_max_times": 0, "manual_dump": false },
  "report": { "max_per_req": 1, "save_sensitive_info": true },
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

**troubleshoot · 压测抓 dump（热更片段示例）：**

```jsonc
{
  "dump": { "auto_max_times": 3, "auto_cooldown_seconds": 300, "manual_dump": false },
  "detector": {
    "token_repeat": { "enabled": true, "on_trigger": ["report", "dump_kv"] }
  }
}
```

**business_default：**

```jsonc
{
  "dump": { "auto_max_times": 0, "manual_dump": false },
  "report": { "max_per_req": 1, "save_sensitive_info": false },
  "detector": {
    "token_repeat": { "enabled": false },
    "logits_finite": { "enabled": false },
    "spec_acceptance": { "enabled": false }
  }
}
```

### Schema 要点

- 无 `dump.enabled`；活跃 = `auto_max_times>0` 或 manual 水位  
- `auto_max_times>0` 与 active `manual_dump` **互斥**  
- 未知 detector key → reload **拒绝并保留旧配置**  
- Report：last-PP TP0；dump：last-PP×全部 TP；各 TP 同 live JSON

## 风险提示

CPU 开销随 detector/dump/热更上升；dump 勿长期开；排完切回 `business_default` 或关 dump。

## forbidden

- 编排端到端排障；解析本地 report/dump

## Related

`detector-sweep` · `investigation` · `analysis` · `ref-kv-dump`
