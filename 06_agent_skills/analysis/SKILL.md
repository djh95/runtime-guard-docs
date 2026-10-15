---
name: runtime-guard-analysis
description: >-
  Offline-only analysis of runtime_guard report JSON and native kv_cache .pt
  dumps: summarize_reports, correlate_incident, verify_request_kv,
  inspect_kv_dump. Emit verify PASS/FAIL as the gate for ref-kv-dump. Never
  emit runtime_config JSON or start a server / force-feed.
---

# runtime_guard analysis（离线读盘）

**类型：原子 · 离线。** 只读磁盘；不改 live config、不起服、不 force-feed。

脚本仓：[runtime-guard-test](https://github.com/djh95/runtime-guard-test) · 定界人读：[02](../../02_problem_localization.md)  
契约：[SKILLS_METADATA.md](../SKILLS_METADATA.md)

```bash
export RG_TEST=/path/to/runtime-guard-test
alias rgpy='PYTHONPATH="$RG_TEST" python -m analysis.scripts'
```

默认 `--report-dir`：`./runtime/report`（可问用户确认）。

## 流程

### Step 0 — 确认 report 根目录

### Step 1 — 汇总

```bash
rgpy.summarize_reports --report-dir ./runtime/report --limit 20
```

空目录 → 停。

### Step 2 — 按 req 关联

```bash
rgpy.correlate_incident --report-dir ./runtime/report --req-id <req_id>
```

关注 `dump_attempted` / `block_ids` / `kv_cache/.../<req_id>/wave_*/<rank_tag>/`。

### Step 3 — report ↔ KV 对账（ref 硬门闩）

```bash
rgpy.verify_request_kv \
  --report ./runtime/report/<type>/report_....json \
  --report-dir ./runtime/report
```

`--kv-dir` 语义是 **rank 目录**（直接含 `.pt`）。明确输出 **PASS / FAIL**（及失败原因）。  
`PASS` 才允许进入 `runtime-guard-ref-kv-dump`。

### Step 4 — 抽查单个 `.pt`（按需）

```bash
rgpy.inspect_kv_dump --path ./runtime/report/kv_cache/<type>/<req_id>/wave_N/<rank_tag>/<file>.pt
```

跨 TP 前核对 `tp_rank` / `num_kv_heads`；层名 natural sort。

### Step 5 — 交付摘要

1. `incident_type`、`req_id`、dump 是否尝试/成功  
2. `verify_result` + `block_ids`  
3. 可提取的 `prompt_token_ids` / `output_token_ids`（需 report 含敏感字段）  
4. 缺口说明  

有 buggy+ref 定界 → 用户/总控再开 `ref-kv-dump` + investigation Q1–Q5（本 skill 不跑对比）。

## 落盘约定

```text
runtime/report/
  <incident_type>/report_*.json          # last-PP TP0
  kv_cache/<incident_type>/<req_id>/wave_<N>/
    request_info.json
    <rank_tag>/*.pt                      # last-PP × 各 TP
```

本请求 `block_ids` 快照，不是全 cache、不是 op 级 dump。

## forbidden

- 输出任何 `runtime_config` / 热更 JSON  
- 拉起推理服务、force-feed、KV buggy↔ref 对比  
- 在 NPU 上 `load` `.pt`；用 msprobe 工具读 native dump  
- 把未合入 detector 当已合入

## Related

`ref-kv-dump`（需本 skill 的 verify PASS）· `investigation` · `config-recommender`
