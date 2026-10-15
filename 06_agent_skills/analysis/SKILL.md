---
name: runtime-guard-analysis
description: >-
  Analyze runtime_guard anomaly reports and per-request KV .pt dumps. Use when
  the user mentions runtime_guard report JSON, kv_cache dumps, dump_kv,
  correlate req_id, nan/inf in KV, or post-mortem of token_repeat /
  logits_finite / spec_acceptance / manual_trigger captures.
---

# runtime_guard analysis（抓现场后）

离线读盘：不改 `runtime_config`、不重跑服务。  
脚本仓：[runtime-guard-test](https://github.com/djh95/runtime-guard-test)。人读定界见手册 [02](../../02_problem_localization.md)。

```bash
export RG_TEST=/path/to/runtime-guard-test
alias rgpy='PYTHONPATH="$RG_TEST" python -m analysis.scripts'
```

默认 `--report-dir`：`./runtime/report`（可问用户确认）。

## 流程

### Step 0 — 确认 report 根目录

用户路径或默认 `./runtime/report` → 后续统一 `--report-dir`。

### Step 1 — 汇总报告

```bash
rgpy.summarize_reports --report-dir ./runtime/report --limit 20
```

有行继续；空目录 → 停。

### Step 2 — 按 req 关联

```bash
rgpy.correlate_incident --report-dir ./runtime/report --req-id <req_id>
```

关注 `dump_attempted` / `block_ids` / `kv_cache/.../<req_id>/wave_*/<rank_tag>/`。

### Step 3 — report ↔ KV 对账

```bash
rgpy.verify_request_kv \
  --report ./runtime/report/<type>/report_....json \
  --report-dir ./runtime/report
```

`--kv-dir` 语义是 **rank 目录**（直接含 `.pt`）。`PASS` 再深入；`FAIL` 先修路径/配额/`on_trigger`。

### Step 4 — 抽查单个 `.pt`（按需）

```bash
rgpy.inspect_kv_dump --path ./runtime/report/kv_cache/<type>/<req_id>/wave_N/<rank_tag>/<file>.pt
```

跨 TP 对比前核对 payload 的 `tp_rank` / `num_kv_heads`。层名 natural sort（`layer_2` < `layer_10`）。

### Step 5 — 对账级结论

1. `incident_type`、`req_id`、`dump_attempted` / `dump_arm_wave`  
2. `block_ids` 与 verify 结论  
3. 关键层 nan/inf / 范围（若跑了 Step 4）  
4. 缺口（无 dump、缺 token ids 等）

### Step 6 — 有 buggy+ref 时定界

交给 `runtime-guard-investigation` 的 **Q1–Q5** + `runtime-guard-ref-kv-dump`。

## 落盘约定

```text
runtime/report/
  <incident_type>/report_*.json          # last-PP TP0
  kv_cache/<incident_type>/<req_id>/wave_<N>/
    request_info.json
    <rank_tag>/*.pt                      # last-PP × 各 TP
```

默认是本请求 `block_ids` 快照，不是全 cache、不是 op 级 dump。

## Do not

- 不改 live config / 不重启（除非用户明确要求）  
- 不假设全量 KV；不在 NPU 上 `load` `.pt`（脚本用 CPU `map_location`）  
- 不用 msprobe 布局工具对 native `kv_cache/*.pt`  
- 勿把 `output_substring` / `slot_*` 当已合入 detector
