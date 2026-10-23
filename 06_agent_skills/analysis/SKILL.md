---
name: runtime-guard-analysis
description: >-
  Offline-only analysis of runtime_guard report JSON and native kv_cache .pt
  dumps: summarize_reports, correlate_incident, verify_request_kv,
  inspect_kv_dump, score_completion_samples. Emit verify PASS/FAIL as the
  gate for ref-kv-dump. Never emit runtime_config JSON or start a server /
  force-feed.
---

# runtime_guard analysis（离线读盘）

**类型：原子 · 离线。** 只读磁盘；不改 live config、不起服、不 force-feed（force-feed = 按报告里的 token id 原样喂给干净服务，禁止再 tokenize 字符串）。

脚本：本仓 [`../scripts/`](../scripts/) · 定界人读：[02](../../02_problem_localization/README.md)  
契约：[SKILLS_METADATA.md](../SKILLS_METADATA.md)

```bash
export RG_DOCS=/path/to/runtime-guard-docs
SCRIPTS="$RG_DOCS/06_agent_skills/scripts"
```

默认 `--report-dir`：`./runtime/report`（可问用户确认）。  
公开对照：本仓 `04_case_studies/cases/Sxx/evidence/`（reports|samples 等）。

## 流程

### Step 0 — 确认 report 根目录

若只有失败证据包（fail-evidence / FE）：同时记下 `samples/` 与 `status.json` 的三层率（trigger/precision/detect）。

### Step 1 — 汇总

```bash
python "$SCRIPTS/summarize_reports.py" --report-dir ./runtime/report --limit 20
```

也接受扁平 `report_*.json`，以及归档别名 `sample_report.json` / `report_sample.json`。

**空 report 目录 ≠ 停：** 若有 completion samples（S07 FAIL+GAP；或 S01 复判 samples），改走 Step 1b。

### Step 1b — 无 report 时的 precision / GAP 评分（keep-set）

```bash
python "$SCRIPTS/score_completion_samples.py" --sample-dir ./samples --json-out samples_score.json
```

关注：`identical_across_requests`、`garbage_mixed_script`、`token0_collapse` / `repeat` / `phrase_repeat`、`detector_gap_hint`。

公开 keep-set 对照（期望 detector + 一句类提示；易混案例）：

| 案例 | 期望 / 提示 |
|------|-------------|
| S01 | dense 常 **FAIL（复现未出现）**：通顺中文 ≠ garbage；排除 CJK 后再计 precision；**≠** S07/S45 的 FAIL+GAP |
| S07 / S45 | `garbage_mixed_script` + detect=0 → **FAIL+GAP**（有异常未检出）；identical-mode 会低估 precision |
| S10p / S11 | `token_repeat`（回收脏尾 / MLA RoPE pad）；≠ 其它 RoPE 半丢族 |
| S22 | 看 `spec_acceptance` 的 rate；samples 可能无 garbage 标签 |
| S23 | always-on 权重置零 → 停在 `token_repeat` detect；**禁止**从 dump 推断「哪条 weight」 |
| S25 / S26 | soft-inverse（按上游修复反向注入）→ `token_repeat` + 问题类提示（half-drop / fp32-mul）；句级复读看 `phrase_repeat`；≠ S11 pad |
| S33 | `token_repeat` + softcap 不完整；≠ overflow/`!!!!` |
| S43 | `token_repeat`；precision 常 newline 塌缩；≠ S23 |
| S47 | `token_repeat`；短语/单字塌缩；≠ attn-scale 族 |
| S48 / S50 | **`logits_finite`**（`!!!!` / token0 塌缩）；≠ residual-drop / skip-silu |
| S06 | MoE 路由类：KV 可能全程 finite —— **finite ≠ 无精度问题**；定界靠复读 + 可选 ref |

有 **真实** precision 且 detect=0 → 交付 **FAIL+GAP**（勿伪造 detector PASS；CJK 误标不算真实 precision）。  
满量 soft-inv 对照表见维护者目录 `_internal/analysis-soft-inv-matrix.md`（不在对外导航）。

### Step 2 — 按 req 关联

```bash
python "$SCRIPTS/correlate_incident.py" --report-dir ./runtime/report --req-id <req_id>
```

关注 `dump_attempted` / `block_ids` / `kv_cache/.../<req_id>/wave_*/<rank_tag>/`。  
容器内 `dump_dir` 与宿主机路径不一致时：把 dump 拉到本地，用 `--kv-dir <rank_dir>` 直指含 `.pt` 的 rank 目录。

### Step 3 — report ↔ KV 对账（ref 硬门闩）

```bash
python "$SCRIPTS/verify_request_kv.py" \
  --report ./runtime/report/<type>/report_....json \
  --report-dir ./runtime/report
# 或：
python "$SCRIPTS/verify_request_kv.py" --report <report.json> --kv-dir <wave_N>/<rank_tag>
```

`--kv-dir` 语义是 **rank 目录**（直接含 `.pt`）。明确输出 **PASS / FAIL**（及失败原因）。  
`PASS` 才允许进入 `runtime-guard-ref-kv-dump`。

`dump_attempted=true` 但本地无 `.pt` → FAIL（路径/配额/`on_trigger`），不是「KV 正常」。

### Step 4 — 抽查单个 `.pt`（按需）

```bash
python "$SCRIPTS/inspect_kv_dump.py" --path ./runtime/report/kv_cache/<type>/<req_id>/wave_N/<rank_tag>/<file>.pt
```

跨 TP 前核对 `tp_rank` / `num_kv_heads`；层名 natural sort。

### Step 5 — 交付摘要

1. `incident_type`、`req_id`、dump 是否尝试/成功；或 GAP 评分摘要  
2. `verify_result` + `block_ids`（有 dump 时）  
3. 可提取的 `prompt_token_ids` / `output_token_ids`（需 report 含敏感字段）  
4. 三层率（若 anomaly）与缺口说明  

有 buggy+ref 定界 → 用户/总控再开 `ref-kv-dump` + investigation 十问（本 skill 不跑对比）。

## 证据完整性（踩坑硬纪律）

- **钉点同跑：** `verify_request_kv` 的 report 与 `--kv-dir` 必须同属一次请求；交付里写明 `req_id` + wave。勿把「目录里碰巧有的 `.pt`」配到另一份 report。  
- **抓前清空工作目录：** 新一轮 dump 前清本轮 `kv_cache` 根，避免 verify 扫到旧 wave。对账进行中勿删本轮路径。  
- **detect=0 ≠ 旧 dump 可用：** 无本轮命中时，可用 `manual_dump` **当场**抓同请求 KV；**禁止**拿历史/他案 dump 顶替。  
- **弱 dump 标明：** output 极短（如 o=1）、或 completion 非目标异常形态 → 在摘要写「弱窗 / 非有效异常 KV」；**不要**据此宣称可进 ref 定界。  
- **空 prompt ids：** 摘要如实写空；勿从字符串补造 ids（交 investigation re-curl）。  
- **交给 ref 前：** 抽查层 `shape`；提醒 history feed 对比用 **`n_prompt+n_output-1`**（整 block 尾部 0 槽不算）；对比脚本会先做数值门闩（NaN/Inf/零范数→数值问题，不算 cos）— 细则在 `ref-kv-dump`。  
- **勿把 NaN cos 当层定位：** 旧摘要若出现 `first_mismatch_idx=0 @ layer_*` 且 `min_cos` 全 NaN，那是排序伪影；交付时写「无有效余弦 / 有效槽全非有限」，勿升格为层名。  
- **空 prompt ids：** 摘要如实写空；注明需 #19285 树重抓或 re-curl，勿 tokenize 补造。  
- **PASS/FAIL 仅 verify 门闩** — keep-set 案例总评用结案四档（见 `investigation`），本 skill 的 PASS/FAIL 不升格为整案结案。

## 落盘约定

```text
runtime/report/
  <incident_type>/report_*.json          # 流水线最后一段的 0 号张量并行卡（last-PP TP0）
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
- 混用不同 run 的 report 与 dump；把弱 dump / 空 ids 补造成可定界证据  
- 在未清目录的残留 wave 上宣称 verify PASS

## Related

`ref-kv-dump`（需本 skill 的 verify PASS）· `investigation` · `config-recommender`
