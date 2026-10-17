# Runtime-Guard Skills Metadata

版本：v2.7  
Skill 列表（**不改名**）：`investigation` · `detector-sweep` · `config-recommender` · `analysis` · `ref-kv-dump`

> **v2.7：** S57 positions×2 before RoPE → `token_repeat` + **L2**；≠ S37。S58 value negate → **`logits_finite`** + **L2**；≠ S51/S47/S52/S54。S59 key×50 → `token_repeat` + **L2**；≠ S49/S51/S54。  
> **v2.6：** S54 key negate → `token_repeat` + **L2**；≠ S47/S51/S52。S55 residual×50 → **`logits_finite`** + **L2**；≠ S31/S38/S48。S56 SwiGLU input negate → **`logits_finite`** + **L2**；≠ S39/S50。  
> **v2.5：** S51 value×50 before FA → `token_repeat` + **L2**；≠ S41/S47/S49。S52 query negate → `token_repeat` + **L2**；≠ S47/S51/S42。S53 lm-head logits÷50 → `token_repeat` + **L2**；≠ S36/S44。  
> **v2.4：** S48 residual negate（`-residual` before add-RMSNorm）→ **`logits_finite`** + **L2**；≠ S31 drop ≠ S38 skip。S49 attn scale ×50 → `token_repeat` + **L2**；≠ S34(=1.0) ≠ S41 post-FA。S50 SwiGLU gate/up half-swap → **`logits_finite`** + **L2**；≠ S39 skip-silu。  
> **v2.3：** S46 penalty sign flip（1/rep + neg freq/pres）→ `token_repeat` + **L2**；≠ S45/S44。S47 K/V swap before FA → `token_repeat` + **L2**；≠ S34/S35/S41。**S45** top-k on `-logits` → **FAIL+GAP**（unique garbage；同 S01/S07）；**S44** 仍 **INVALID** vacated。  
> **v2.2：** S42 `-cos_sin` wrong RoPE phase → `token_repeat` + **L2**；≠ S37/S40/S25/S28。S43 embed ×100 → `token_repeat` + **L2**；score `newline_collapse`；≠ S23/S41。**S44** `logits.zero_()` → **BLOCKED / invalid-synthetic**（PRINCIPLES §2 amplifier；非 skills win）。  
> **v2.1：** S39 SwiGLU skip-silu → **`logits_finite`** + **L2**；≠ S26/S31/S38。S40 RoPE skip（unrotated Q/K）→ `token_repeat` + **L2**；≠ S25/S28/S37。S41 post-FA attn `mul_(1000)` → **`logits_finite`** + **L2**；≠ S34/S14/S35。  
> **v2.0：** S36 temp-scale blowup（÷50）→ `token_repeat` + **L2**；score `id_echo`/`unique_garbage`（identical-mode 低估）。S37 positions→0 before RoPE → `token_repeat` + **L2**；≠ S25/S28/S11。S38 RMSNorm identity skip → **`logits_finite`**（`!!!!`）+ **L2**；≠ S26/S31/S20（S20 主靠 `token_repeat`）。  
> **v1.9：** S34 attn scale drop（1/sqrt(d)→1.0）→ `token_repeat` + **L2**（wrong attn temp；unique garbage）；≠ S20/S32/S33。S35 causal-off（causal=False + mask=None）→ `token_repeat` + **L2**（future leak）；≠ S34。  
> **v1.8：** S32 FIA FULL-graph pad（#7144）→ `token_repeat` + **L2**；score `pad_echo`（unique garbage，≠ identical-mode）；≠ S14。S33 incomplete softcap（÷cap+tanh skip *cap）→ `token_repeat` + **L2**；≠ S20 overflow。  
> **v1.7：** S29/S30/S31（logits fp16 demote / null-block KV dirt / residual drop）→ `token_repeat` + **L2 class-hint**；≠ S20/S26/S01/S10。  
> **v1.6：** S25/S26/S28 soft-inv（RoPE 半写丢 / RMSNorm fp32-mul / neox→interleaved）→ `token_repeat` + **L2**；score `phrase_repeat`。≠ S11 pad。  
> **v1.5：** S23/S24 权重·量化 always-on → **detect-only**（`token_repeat`）；score 勿因混有 garbage 标签误报 GAP；≠ S07。  
> **v1.4：** S22 spec resample 无 SALT → `spec_acceptance`；≠ S05/S20。  
> **v1.3：** S20 softcap/softmax 溢出 → `token_repeat`；score 不把纯 bang 塌缩标 GAP。  
> **v1.2：** 三层率、根因 class 表、finite-garbage GAP、`score_completion_samples`。

> 本文是职责契约（给人 / Agent 对齐用），**不是** RPC schema。  
> 输入输出用「逻辑字段」描述即可；对话里用自然语言收集，勿伪造 JSON 信封。

## 设计约束

1. **编排 vs 原子**：`investigation` 只串联与定界交付；底层工序在原子 skill。  
2. **在线 vs 离线**：配置类 skill 不做磁盘解析；`analysis` / `ref-kv-dump` 不输出 runtime_config JSON。  
3. **ref 门闩**：`ref-kv-dump` 前必须已有 `verify_request_kv` PASS（本轮跑 `analysis`，或用户出示 PASS 证据）；禁止跳过校验。  
4. **配置唯一源**：正式阈值 / 配额 / `on_trigger` / cooldown **只**来自 `config-recommender`；`detector-sweep` 仅极简筛查模板。  
5. **委派可复述**：编排侧可粘贴下游产出的配置，**禁止自创**阈值与配额。

## 名称与类型

| Skill | 类型 | 一句话 |
|-------|------|--------|
| investigation | 编排 | 端到端 triage → 委派 → Q1–Q5 定界交付 |
| detector-sweep | 原子 · 在线配置 | 未定类：临时三键只 report |
| config-recommender | 原子 · 在线配置 | 正式排障 / 业务默认配置唯一来源 |
| analysis | 原子 · 离线读盘 | report/dump 汇总、关联、verify、inspect |
| ref-kv-dump | 原子 · 标杆+对比 | force-feed 抓 ref + KV 首分歧 |

原子 skill 可独立调用；**勿从原子 skill 反调 investigation**（靠 description / README 约定，非强制）。

---

## 1. investigation

**触发：** 要完整走一遍 Guard 排障，或不知道下一步。

**can_do**

- Triage（手册 02）：Hang/OOM/启动 crash 等 → 终止并说明原因  
- 收集开场输入：现象、版本、拓扑、能否压测、有无清洁标杆、本地 report/dump 路径、谁起服  
- 委派：未定类 → sweep；定类 → recommender；已有产物 → analysis；verify=PASS 且可标杆 → ref-kv-dump  
- 汇总下游结果，填 Q1–Q5 **定界交付模板**；区分「已定界」vs「无法根因定位」

**forbidden**

- 自创 runtime_config 阈值 / dump 配额 / cooldown / `on_trigger`（须来自 sweep 或 recommender 产出）  
- 自行实现离线解析或 force-feed / 对比脚本流程（委派 analysis / ref）  
- 承诺定位到算子 / 内核 / 具体提交

**逻辑输入：** symptom, version, topology, can_pressure_test, has_clean_ref_env, local_artifact_path?  
**逻辑输出：** triage_result, delegated 摘要, delimitation_template, conclusion, next_step

**依赖：** 可调用四个原子 skill；无上游。

---

## 2. detector-sweep

**触发：** 现象未定类，要临时多开已合入 detector **只 report**。

**can_do**

- 输出极简 sweep JSON：已合入 detector `enabled` + `on_trigger:["report"]`；`auto_max_times:0` / 关 manual dump  
- 允许开关级字段：`report.max_per_req`、`save_sensitive_info`（完整热更文件需要）  
- 风险提示：临时排障，禁止业务长期开；命中后交给 `config-recommender`

**forbidden**

- 业务调优：window / 阈值 / ignore_token_ids / auto_max_times>0 / cooldown  
- 开启 `dump_kv`  
- 解析本地 report/dump（读盘 → analysis）

**逻辑输入：** version（过滤该版本不存在的 detector；非 MTP 勿开 spec）  
**逻辑输出：** sweep JSON 文本, warning, follow_up → recommender

---

## 3. config-recommender

**触发：** 现象已明确，要正式排障配置或业务默认全关。

**can_do**

- `mode=troubleshoot`：detector 开关、阈值、window、`on_trigger`、auto_max_times、cooldown、盘预算  
- `mode=business_default`：detector 全关、dump 关（fully_off / 常态）  
- 热更片段 + CPU/磁盘风险说明  

**forbidden**

- 端到端编排；读盘解析 report/dump

**逻辑输入：** symptom, version, mode, disk_remaining_gb?  
**逻辑输出：** full JSON, hot_reload snippet, risk_notes, parameter_explain

---

## 4. analysis

**触发：** 本地已有 report（±dump），或仅有 completion samples（FAIL+GAP / precision 层）。

**can_do**

- `summarize_reports` / `correlate_incident` / `verify_request_kv` / `inspect_kv_dump`（按需）  
- `score_completion_samples`（无 report 时的 garbage / identical 评分）  
- 提取 prompt/output token ids、incident 类型等现场字段  
- `verify_result=PASS|FAIL`（ref 的硬门闩）；GAP 时输出 `detector_gap_hint` 而非伪 PASS

**forbidden**

- 输出 runtime_config / 热更 JSON  
- 拉起推理服务、force-feed、标杆对比（→ ref-kv-dump）  
- 把 empty report 直接当成「无异常」而不看 samples

**逻辑输入：** report_dir, optional_dump_dir?, optional_sample_dir?  
**逻辑输出：** verify_result, request_list 摘要, artifact_check_note, optional gap_score

---

## 5. ref-kv-dump

**触发：** buggy 侧已 verify PASS，要同 token force-feed 抓 ref 并做 KV 首分歧。

**can_do**

- 用报告 token ids force-feed（禁止字符串重 tokenize / 禁止标杆自行生成）  
- 同模型 / 拓扑 / **同 MODE** 清洁实例 + native `dump_kv`  
- `compare_kv_similarity` / `locate_first_divergence` / `compare_per_layer`；解读对齐 Q1–Q5

**forbidden**

- 无 verify PASS 证据仍执行  
- 重复实现 `verify_request_kv`  
- 输出 runtime_config JSON

**逻辑输入：** verify PASS 证据, buggy token ids / report 路径, topology, model_mode  
**逻辑输出：** ref_dump_path, kv_compare 摘要, warnings

---

## 维护规则

| 变更 | 改谁 |
|------|------|
| 已有 detector 算法 / 推荐阈值 | `config-recommender`（+ 手册 03） |
| 新增已合入 detector | `config-recommender` + `detector-sweep` |
| report JSON schema | `analysis`（+ 必要时 recommender 字段说明） |
| 仅文档措辞、代码参数不变 | 只改手册，skill 可不改 |

脚本 CLI 变更 → 同步本目录 + [runtime-guard-test](https://github.com/djh95/runtime-guard-test) 的 `analysis/skill/`。
