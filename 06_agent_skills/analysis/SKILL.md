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

**类型：原子 · 离线。** 只读磁盘；不改 live config、不起服、不 force-feed。

脚本仓：[runtime-guard-test](https://github.com/djh95/runtime-guard-test) · 定界人读：[02](https://github.com/djh95/runtime-guard-docs/blob/main/02_problem_localization.md)  
契约：[SKILLS_METADATA.md](./SKILLS_METADATA.md)

```bash
export RG_TEST=/path/to/runtime-guard-test
alias rgpy='PYTHONPATH="$RG_TEST" python -m analysis.scripts'
```

默认 `--report-dir`：`./runtime/report`（可问用户确认）。  
Anomaly 证据树：`tests/build-anomaly-env/fail-evidence/Sxx/`（`status.json` / `layers.json` / `WHY_*.md` / reports|samples）。

## 流程

### Step 0 — 确认 report 根目录

若只有 fail-evidence：同时记下 `samples/` 与 `status.json` 的三层率（trigger/precision/detect）。

### Step 1 — 汇总

```bash
rgpy.summarize_reports --report-dir ./runtime/report --limit 20
```

也接受扁平 `report_*.json`，以及归档别名 `sample_report.json` / `report_sample.json`。

**空 report 目录 ≠ 停：** 若有 completion samples（S01/S07 FAIL+GAP），改走 Step 1b。

### Step 1b — 无 report 时的 precision / GAP 评分

```bash
rgpy.score_completion_samples --sample-dir ./samples --json-out samples_score.json
```

关注：`identical_across_requests`、`garbage_mixed_script`、`token0_collapse` / `repeat` / `phrase_repeat`、`detector_gap_hint`。  
- 纯 `!!!!…` / token0 塌缩（S20 overflow class）→ 期望已有 `token_repeat` report；**不是** GAP。  
- Spec 接受率异常（S22）→ 看 `spec_acceptance` report 的 rate 字段；samples 可能无 garbage 标签（分布性 precision）。  
- 权重/量化 always-on（S23/S24）→ **停在 detect**：`token_repeat` report 即够；**禁止**从 dump/ref 推断「哪条 weight/scale」。  
- Soft-inv RoPE/RMSNorm（S25/S26/S28）→ `token_repeat` + **L2 class-hint**（half-drop / fp32-mul / neox→interleaved）；句级复读看 `phrase_repeat`；≠ S11 pad。有 report 时勿因短标签空而宣称「无 precision」。  
- Logits fp16 demote（S29）→ `token_repeat` + **L2 cast**；≠ S20/S26。Null-block KV dirt（S30）→ `token_repeat` + **L2 KV**（可 verify/ref）；≠ S01/S10。Residual drop（S31）→ 强 `phrase_repeat`/identical；**L2** ≠ S26。  
- FIA FULL-graph pad（S32 #7144）→ `token_repeat` + **L2**；precision 常为 **unique** `pad_echo`（`wN_M` / `_0_0_0`），identical-mode 会低估；≠ S14。  
- Incomplete softcap（S33）→ `token_repeat` + **L2**（÷cap+tanh skip *cap）；≠ S20 overflow/`!!!!`。  
- Attn scale drop（S34）→ `token_repeat` + **L2**（wrong attn temp）；precision 常 **unique** digit/junk；≠ S20/S32/S33。  
- Causal-off（S35）→ `token_repeat` + **L2**（future leak）；强 `phrase_repeat`/prompt-echo；≠ S34。  
- Temp-scale blowup（S36）→ `token_repeat` + **L2**；precision 常 **unique** `id_echo`/`unique_garbage`；勿因 identical_mode 低判「无 precision」。≠ S29/S20。  
- Positions→0（S37）→ `token_repeat` + **L2**；≠ S25/S28/S11。  
- RMSNorm identity skip（S38）→ **`logits_finite`**（`!!!!`/`token0_collapse`）；**L2** ≠ S26/S31；勿当成「仅 S20 softcap」。  
- SwiGLU skip-silu（S39）→ **`logits_finite`** + **L2**；≠ S26/S31/S38。  
- RoPE skip（S40）→ `token_repeat` + **L2**；强 `phrase_repeat`；≠ S25/S28/S37。  
- Post-FA attn `mul_(1000)`（S41）→ **`logits_finite`** + **L2**；≠ S34（softmax scale）/S14/S35。  
- RoPE phase negate（S42）→ `token_repeat` + **L2**；≠ S37/S40/S25/S28。  
- Embed ×100（S43）→ `token_repeat` + **L2**；precision 常 **`newline_collapse`**；≠ S23/S41。  
- Logits `zero_()`（S44）→ **invalid-synthetic / BLOCKED**（放大器）；归档勿当 skills win。  
- Top-k on `-logits`（S45）→ **FAIL+GAP**：unique `garbage_mixed_script` + detect=0（同 S01/S07）；identical-mode 低估勿判「无 precision」。  
- Penalty sign flip（S46）→ `token_repeat` + **L2**；digit/`1.1.1…`；≠ S45/S44。  
- K/V swap（S47）→ `token_repeat` + **L2**；短语/单字塌缩；≠ S34/S35/S41。  
- Residual negate（S48）→ **`logits_finite`** + **L2**；`!!!!`/`token0_collapse`；≠ S31 drop ≠ S38 skip。  
- Attn scale ×50（S49）→ `token_repeat` + **L2**；precision 常 unique/`1.1.1…`；≠ S34(=1.0) ≠ S41 post-FA。  
- SwiGLU half-swap（S50）→ **`logits_finite`** + **L2**；`!!!!`；≠ S39 skip-silu。  
- Value ×50 before FA（S51）→ `token_repeat` + **L2**；≠ S41/S47/S49。  
- Query negate（S52）→ `token_repeat` + **L2**；≠ S47/S51/S42。  
- LM-head logits ÷50（S53）→ `token_repeat` + **L2**；≠ S36 post-temp ≠ S44 amplifier。  
- Key negate（S54）→ `token_repeat` + **L2**；≠ S47/S51/S52。  
- Residual ×50（S55）→ **`logits_finite`** + **L2**；≠ S31/S38/S48。  
- SwiGLU input negate（S56）→ **`logits_finite`** + **L2**；≠ S39/S50。  
- Positions ×2（S57）→ `token_repeat` + **L2**；≠ S37。  
- Value negate（S58）→ **`logits_finite`** + **L2**；≠ S51/S47/S52/S54。  
- Key ×50（S59）→ `token_repeat` + **L2**；≠ S49/S51/S54。  
- Query ×50（S60）→ `token_repeat` + **L2**；≠ S52/S49/S51/S59。  
- Hidden ×50（S61）→ `token_repeat` + **L2**；≠ S53/S43。  
- Pre-RMSNorm x×50（S62）→ **`logits_finite`** + **L2**；≠ S26/S38/S48/S55。  
- Attn-out negate（S63）→ **`logits_finite`** + **L2**；≠ S41。  
- Residual ÷50（S64）→ `token_repeat` + **L2**；≠ S48/S55。  
- Logits ×50（S65）→ `token_repeat` + **L2**；≠ S53/S36。  
- RMSNorm weight negate（S66）→ **`logits_finite`** + **L2**；≠ S26/S38/S48/S55/S62。  
- SwiGLU out negate（S67）→ **`logits_finite`** + **L2**；≠ S39/S50/S56。  
- Attn scale ÷50（S68）→ `token_repeat` + **L2**；≠ S34/S49。  
- Embed negate（S69）→ **`logits_finite`** + **L2**；≠ S43。  
- Variance eps ×1000（S70）→ `token_repeat` + **L2**；≠ S26/S38/S66。  
- RMSNorm weight ×50（S71）→ **`logits_finite`** + **L2**；≠ S66。  
- SwiGLU out ×50（S72）→ **`logits_finite`** + **L2**；≠ S39/S50/S56/S67。  
- RMSNorm x negate（S73）→ **`logits_finite`** + **L2**；≠ S48/S62。  
- RMSNorm weight ÷50（S74）→ `token_repeat` + **L2**；≠ S66/S71。  
- Hidden ÷50（S75）→ `token_repeat` + **L2**；≠ S61/S53/S65。  
- SwiGLU input ×50（S76）→ **`logits_finite`** + **L2**；≠ S39/S50/S56/S67/S72。  
- Variance eps ÷1000（S77）→ `token_repeat` + **L2**；≠ S70。  
- RMSNorm x ÷50（S78）→ `token_repeat` + **L2**；≠ S62/S73。  
- Cos/sin ×50（S79）→ `token_repeat` + **L2**；≠ S37/S40/S42/S25/S28。  
- Embed ÷50（S80）→ `token_repeat` + **L2**；≠ S43/S69。  
- SwiGLU input ÷50（S81）→ `token_repeat` + **L2**；≠ S39/S50/S56/S76。  
- Cos/sin ÷50（S82）→ `token_repeat` + **L2**；≠ S37/S40/S42/S79。  
- Attn-out ×50（S83）→ `token_repeat` + **L2**；≠ S41/S63。  
- Positions ÷2（S84）→ `token_repeat` + **L2**；≠ S37/S57。  
- Temp ÷50（S85，post-temp×50）→ `token_repeat` + **L2**；≠ S36；需 temperature>0。  
- RMSNorm-out negate（S86）→ **`logits_finite`** + **L2**；≠ S73/S66。  
- RMSNorm-out ×50（S87）→ **`logits_finite`** + **L2**；≠ S62/S86。  
- Residual-post negate（S88）→ **`logits_finite`** + **L2**；≠ S48/S86。  
- RMSNorm-out ÷50（S89）→ `token_repeat` + **L2**；≠ S87/S78。  
- Residual-post ×50（S90）→ **`logits_finite`** + **L2**；≠ S55/S64/S88。  
- Residual-post ÷50（S91）→ `token_repeat` + **L2**；≠ S90/S64/S88。  
- Temp-skip（S92）→ `token_repeat` + **L2**；≠ S36/S85；需 T>0；**identical-mode precision=0 仍可 PASS**（per-req detect）。  
- Residual←normed-x（S93）→ `token_repeat` + **L2**；≠ S31/S94/S88–S91。  
- Residual↔x swap（S94）→ **`logits_finite`** + **L2**；≠ S31/S93/S88。  
- Temp-double（S95）→ `token_repeat` + **L2**；≠ S36/S85/S92；需 T>0。  
- RMSNorm-weight=ones（S96）→ `token_repeat` + **L2**；≠ S66/S71/S74；**identical-mode precision=0 仍可 PASS**（per-req detect）。  
- Residual-leak-add（S97）→ **`logits_finite`** + **L2**；≠ S31/S93/S94/S88–S91。  
- Min_p-skip（S98）→ `token_repeat` + **L2**；≠ S36/S85/S92/S95/S46；需 T>0；**precision=0 仍可 PASS**。  
- Top_p-skip（S99）→ `token_repeat` + **L2**；≠ S45/S98/temp；需 T>0；**precision=0 仍可 PASS**（detect≈45）。  
- RMSNorm-bias=weight（S100）→ `token_repeat` + **L2**；≠ S66/S71/S74/S96。  
- Cos/sin-half-swap（S101）→ `token_repeat` + **L2**；≠ S42/S79–S82/S40/S25/S28。  
- RMSNorm-out-abs（S102）→ `token_repeat` + **L2**；≠ S86/S87–S89。  
- SwiGLU-gate-only（S103）→ `token_repeat` + **L2**；≠ S39/S50/S56–S81；**identical-mode precision=0 仍可 PASS**（detect=48）。  
- Rope-skip-key（S104）→ `token_repeat` + **L2**；≠ S40/S25/S28/S101。  
- Rope-skip-query（S105）→ `token_repeat` + **L2**；≠ S104/S40/S25/S28/S101。  
- Residual-post-abs（S106）→ `token_repeat` + **L2**；≠ S88/S90–S91/S102。  
- SwiGLU-up-only（S107）→ `token_repeat` + **L2**；≠ S103/S39/S50。  
- Hidden-abs（S108）→ `token_repeat` + **L2**；≠ S61/S75。  
- Value-abs（S109）→ `token_repeat` + **L2**；≠ S58/S51；**identical-mode precision=0 仍可 PASS**（detect=24）。  
- RMSNorm-weight-abs（S110）→ `token_repeat` + **L2**；≠ S66/S71/S74/S96/S100。  
- Key-abs（S111）→ `token_repeat` + **L2**；≠ S54/S59/S109。  
- Embed-abs（S112）→ `token_repeat` + **L2**；≠ S69/S43/S80。  
- Cos/sin-abs（S113）→ `token_repeat` + **L2**；≠ S42/S79–S82/S101/S40；**identical-mode precision=0 仍可 PASS**（detect=48）。  
- Query-abs（S114）→ `token_repeat` + **L2**；≠ S52/S60/S109/S111。  
- SwiGLU-out-abs（S115）→ `token_repeat` + **L2**；≠ S67/S72/S103/S107。  
- RMSNorm-x-abs（S116）→ `token_repeat` + **L2**；≠ S73/S62/S78/S102。  
- Query-scale-down（S117）→ `token_repeat` + **L2**；≠ S60/S52/S114。  
- Key-scale-down（S118）→ `token_repeat` + **L2**；≠ S59/S54/S111。  
- Residual-pre-abs（S119）→ `token_repeat` + **L2**；≠ S48/S55/S64/S106。  
- RMSNorm-weight=zeros（S120）→ `token_repeat` + **L2**；≠ S96/S66/S71/S74/S110。  
- SwiGLU-input-abs（S121）→ `token_repeat` + **L2**；≠ S56/S76/S81/S115；**identical-mode precision=0 仍可 PASS**（detect=48）。  
- Logits-abs（S122）→ `token_repeat` + **L2**；≠ S53/S65/S108。  
- RMSNorm-bias=-weight（S123）→ `token_repeat` + **L2**；≠ S100/S66/S120。  
- Penalty-skip（S124）→ `token_repeat` + **L2**；≠ S46/S98/S99；**identical-mode precision=0 仍可 PASS**（detect=48）。  
- Residual-leak-sub（S125）→ **`logits_finite`** + **L2**；≠ S97/S93/S94/S31。  
- Hidden-zeros（S126）→ `token_repeat` + **L2**；≠ S61/S75/S108/S122。  
- Embed-zeros（S127）→ `token_repeat` + **L2**；≠ S69/S43/S80/S112。  
- Cos/sin-zeros（S128）→ `token_repeat` + **L2**；≠ S42/S79–S82/S101/S113。  
- `garbage_mixed_script` + detect=0 → **FAIL+GAP**（S01/S07/S45）。若已有 `token_repeat` report，勿因 samples 里偶发 garbage 标签宣称 GAP。  
有 precision 且 detect=0 → 交付 **FAIL+GAP**（勿伪造 detector PASS）。

### Step 2 — 按 req 关联

```bash
rgpy.correlate_incident --report-dir ./runtime/report --req-id <req_id>
```

关注 `dump_attempted` / `block_ids` / `kv_cache/.../<req_id>/wave_*/<rank_tag>/`。  
容器内 `dump_dir` 与宿主机路径不一致时：把 dump 拉到本地，用 `--kv-dir <rank_dir>` 直指含 `.pt` 的 rank 目录。

### Step 3 — report ↔ KV 对账（ref 硬门闩）

```bash
rgpy.verify_request_kv \
  --report ./runtime/report/<type>/report_....json \
  --report-dir ./runtime/report
# 或：
rgpy.verify_request_kv --report <report.json> --kv-dir <wave_N>/<rank_tag>
```

`--kv-dir` 语义是 **rank 目录**（直接含 `.pt`）。明确输出 **PASS / FAIL**（及失败原因）。  
`PASS` 才允许进入 `runtime-guard-ref-kv-dump`。

`dump_attempted=true` 但本地无 `.pt` → FAIL（路径/配额/`on_trigger`），不是「KV 正常」。

### Step 4 — 抽查单个 `.pt`（按需）

```bash
rgpy.inspect_kv_dump --path ./runtime/report/kv_cache/<type>/<req_id>/wave_N/<rank_tag>/<file>.pt
```

跨 TP 前核对 `tp_rank` / `num_kv_heads`；层名 natural sort。  
MoE 路由类（S06/S16–S19）KV 可能全程 finite —— **finite ≠ 无精度问题**；定界仍靠 token 复读 + 可选 ref。

### Step 5 — 交付摘要

1. `incident_type`、`req_id`、dump 是否尝试/成功；或 GAP 评分摘要  
2. `verify_result` + `block_ids`（有 dump 时）  
3. 可提取的 `prompt_token_ids` / `output_token_ids`（需 report 含敏感字段）  
4. 三层率（若 anomaly）与缺口说明  

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
