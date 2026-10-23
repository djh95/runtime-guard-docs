# Runtime-Guard Skills Metadata

版本：v5.17  
Skill 列表：`investigation` · `detector-sweep` · `config-recommender` · `analysis` · `ref-kv-dump` · **`msprobe-dump`** · **`build-anomaly-env`** · **`apply-mrv1-patch`** · **`apply-v030-mrv2-patch`**

## Changelog（摘要）

按波次归纳；细案例 ID / 失败证据包（FE）细节不在此逐条堆叠（完整评测矩阵不在本仓）。

离线脚本入口：本仓 [`scripts/`](./scripts/)。

- **v5.17（现行）** — **跨环境标杆**：必现案先问「他环境是否正常」；若有异常环境+正常环境，可分环境抓 buggy/ref dump；对比前**必须**核对**权重 MD5（或等价）**与**代码 commit（及关键 patch/overlay）一致**，不一致则不能当干净标杆。落点：`investigation` / `ref-kv-dump`（S50 / `logits_finite` 等尤为相关）。  
- **v5.16** — KV 对比**数值门闩优先**：每个 (token, layer) 先扫 NaN/Inf/零范数 → 标 **数值问题**、**不算余弦**；相似度只在干净格上算；禁止把 NaN 当「最差 cos」排序成伪 `idx=0 @ layer_*`。有效槽全非有限 → 不定层，只记「有效槽全非有限」。脚本：`scripts/_lib.py` / `compare_*` / `locate_first_divergence` / `stitch_kv`。落点：`ref-kv-dump` / `investigation` / `analysis` / `scripts`。  
- **v5.15** — **收回** v5.14「logits→跳过 KV」：`logits_finite` 后 **仍先** `dump_kv`（有效槽有限/Inf/NaN；未用槽**分级**：有限非 0=卫生/通常不致坏结果，Inf/NaN=可影响结果）；标杆须未炸；必现优先、非必现 `manual_dump`。**`msprobe-dump` 殿后**（全程挂钩、开销大）。NaN cos 仍不定层。落点：`investigation` / `ref-kv-dump` / `msprobe-dump` / README / `02` / `04`。  
- **v5.14** — 引入 **`msprobe-dump`**（`task=statistics`，eager only）；曾写「logits→跳过 KV」（**已被 v5.15 纠正**）。  
- **v5.13** — `--feed=history` 对比跨度 **`n_prompt+n_output-1`**（禁按 p+o 全长→末位假分歧/伪层定位）；空 prompt 优先 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) 重抓或 re-curl，禁 tokenize 补造。落点：`ref-kv-dump` / `investigation` / `analysis`。  
- **v5.12** — KV 执行纪律：抓前**清空**本轮 `kv_cache`；对比**先 shape**；整 block dump、未用槽常为 0 → **只比有效 token**（禁全容量余弦）。落点：`ref-kv-dump`（主）+ `investigation` / `analysis` / `scripts/README`。  
- **v5.11** — 踩坑原则入库：keep-set **结案四档**（≠ PASS/FAIL/GAP 总评）；**钉点同跑** / 禁混用 run；**有效异常 KV**（弱窗不可对账）；**全 NaN cos ≠ 层定位**；多组验证；无证据留空；压测上限 ~1h；`manual_dump` 抓未检出异常。落点：`investigation` / `analysis` / `ref-kv-dump` / `build-anomaly-env`。  
- **v5.10** — 构造 skill：`build-anomaly-env`（origin-faithful overlay / 三层率 / HARD·DEFER；术语主页）；排障五件套 + 接线 skills 不变。  
- **v5.9** — 接线 skills：`apply-mrv1-patch`（`05_mrv1_backport`）· `apply-v030-mrv2-patch`（`05_v030_backport`）；排障五件套不变。  
- **v5.8** — ones/zeros 收尾；多为 `token_repeat` + 问题类提示（L2）。
- **v5.0–v5.7** — soft-inverse（按上游修复反向注入）矩阵扩展。
- **v4.x** — abs / scale / skip / half-swap 波；偶发走 `logits_finite`。
- **v3.x** — mag/polarity 算子族铺开。
- **v2.x** — 典型 keep 案落地（如 S45 GAP、S43/S48/S50 PASS、S22 spec）。
- **v1.x** — 三层率与 `score_completion_samples`；早期 soft-inverse / weight / overflow / pad。

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
| investigation | 编排 | 端到端 triage → 委派 → 十问定界交付 |
| detector-sweep | 原子 · 在线配置 | 未定类：临时三键只 report |
| config-recommender | 原子 · 在线配置 | 正式排障 / 业务默认配置唯一来源 |
| analysis | 原子 · 离线读盘 | report/dump 汇总、关联、verify、inspect |
| ref-kv-dump | 原子 · 标杆+对比 | force-feed（按报告 token id 原样喂干净服务）抓 ref + KV 首分歧 |
| msprobe-dump | 原子 · 算子 dump | KV 分流后（殿后）statistics dump（eager only）；扫首坏算子 |
| build-anomaly-env | 构造 · 评测基建 | origin-faithful overlay 场景；三层率；禁合成放大器 |
| apply-mrv1-patch | 运维 · 接线 | 多 release × MRV1 → `05_mrv1_backport` |
| apply-v030-mrv2-patch | 运维 · 接线 | v0.30 × MRV2 → `05_v030_backport` |

原子 skill 可独立调用；**勿从原子 skill 反调 investigation**（靠 description / README 约定，非强制）。

---

## 1. investigation

**触发：** 要完整走一遍 Guard 排障，或不知道下一步。

**can_do**

- Triage（手册 02）：Hang/OOM/启动 crash 等 → 终止并说明原因  
- 收集开场输入：现象、版本、拓扑、能否压测、有无清洁标杆、本地 report/dump 路径、谁起服  
- 委派：未定类 → sweep；定类 → recommender；已有产物 → analysis；verify=PASS 且可标杆 → ref-kv-dump；**`logits_finite` 亦先 ref-kv**（有限性 + 未用槽分级），再视需要 **msprobe-dump（殿后）**  
- 汇总下游结果，填十问 **定界交付模板**（KV 路径）或（殿后）msprobe 首坏算子摘要；区分「已定界」vs「无法根因定位」  
- keep-set **结案四档** + 证据完整性（钉点同跑 / 有效异常 KV / 数值问题禁伪定位 / 未用槽分级 / 无证据留空）

**forbidden**

- 自创 runtime_config 阈值 / dump 配额 / cooldown / `on_trigger`（须来自 sweep 或 recommender 产出）  
- 自行实现离线解析或 force-feed / 对比脚本流程（委派 analysis / ref）  
- 仅凭 Guard KV / 坏输出 **跳承诺**算子/内核/提交（msprobe `dump.json` 首非有限统计可写算子名，仍勿升格成上游 commit）  
- 混用不同 run；用弱 dump / 数值问题或无有效余弦伪写层定位；用 PASS/FAIL/GAP 当案例 headline 结案  
- `logits_finite` 后跳过 KV 直开 msprobe；把未用槽有限非 0 与 Inf/NaN 混成同等严重

**逻辑输入：** symptom, version, topology, can_pressure_test, has_clean_ref_env, local_artifact_path?  
**逻辑输出：** triage_result, delegated 摘要, delimitation_template, conclusion, next_step

**依赖：** 可调用原子 skill（含 `msprobe-dump`）；无上游。

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
- `mode=business_default`：detector 全关、dump 关（全关旁路 / 常态）  
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
- 混用不同 run 的 report/dump；把弱 dump / 空 ids 补造为可定界证据

**逻辑输入：** report_dir, optional_dump_dir?, optional_sample_dir?  
**逻辑输出：** verify_result, request_list 摘要, artifact_check_note, optional gap_score

---

## 5. ref-kv-dump

**触发：** buggy 侧已 verify PASS，要同 token force-feed 抓 ref 并做 KV 首分歧。

**can_do**

- 用报告 token ids force-feed（禁止字符串重 tokenize / 禁止标杆自行生成）  
- 同模型 / 拓扑 / **同 MODE** 清洁实例 + native `dump_kv`  
- **跨环境标杆**：必现且他环境正常时，分环境抓 buggy/ref；对比前核权重 MD5 + 代码 commit/overlay  
- `compare_kv_similarity` / `locate_first_divergence` / `compare_per_layer`；解读对齐十问  
- 校验有效异常 KV / 数值门闩后拒绝无有效余弦的**层**伪定位；报有效槽 Inf/NaN；未用槽分级（有限非 0 vs Inf/NaN）  
- 抓前清 `kv_cache`；对比先 shape；history 用 `p+o-1`；只比有效 token（整 block 未用槽不算进余弦）  
- `logits_finite` 路径：标杆须未炸；短 output 仍做有限性/未用槽分级

**forbidden**

- 无 verify PASS 证据仍执行  
- 重复实现 `verify_request_kv`  
- 输出 runtime_config JSON  
- 弱 dump / 数值问题格上硬算 cos / history 末位假分歧写成层定位；混用不同 run  
- 未清目录用旧 dump；跳过 shape；按全 block 容量算余弦；tokenize 冒充 prompt ids  
- `logits_finite` 后跳过本 skill；未用槽有限非 0 与 Inf/NaN 混判  
- 跨环境未核权重 MD5 / 代码 commit 就把他环境当干净标杆

**逻辑输入：** verify PASS 证据, buggy token ids / report 路径, topology, model_mode  
**逻辑输出：** ref_dump_path, kv_compare 摘要（含 finite/unused 分级）, warnings

**何时不调：** 无 verify PASS / 无可用 dump；Hang 等 triage 已终止。`logits_finite` **仍调**本 skill（msprobe 殿后另开）。

---

## 6. msprobe-dump

**触发：** KV（ref-kv）已分流后，仍要 dump 算子 I/O **统计值**找首坏算子（`logits_finite` / 非有限数值炸）。**殿后、开销大。**

**can_do**

- 写 `task=statistics` / `summary_mode=statistics` / 默认 `level=L1` 的 config  
- 经 vllm-ascend `--additional-config.dump_config_path`（或 `dump_config`）启用；**必须 `--enforce-eager`**  
- 指导读 `dump.json`（Max/Min/Mean/Norm）找首个非有限/爆炸条目  
- 可选收窄 `list`/`scope`、钉 `request_id`

**forbidden**

- 图模式 / aclgraph 当默认路径  
- 默认 `task=tensor` 全量落盘  
- 把 msprobe 产物当 Guard `dump_kv` 对比源  
- 未装 `mindstudio-probe` 却假装已 dump

**逻辑输入：** logits_finite report 路径?, model/topo, dump_path, optional request_id  
**逻辑输出：** dump_path, first_bad_op?, notes

**依赖：** 容器已 `pip install mindstudio-probe`；vllm-ascend 带 `dump_config_path` 接线。

---

## 7. build-anomaly-env

**触发：** 要挖/建 anomaly 评测环境（overlay），或抬 origin-faithful 复现率。

**can_do**

- 按真实修复 PR 挖 typed 候选；写 overlay-only 故障（测试仓 `tests/build-anomaly-env/`）  
- 列 allowed/forbidden knobs；用合法 knobs 抬 trigger/precision；记 original vs tuned rate  
- 强制三层分计 + bug 路径开火日志；打包 SPEC / overlay / 上游 PR / 样本 / 三层  
- HARD/DEFER 难 bug，改挖新候选；`synthetic/` 仅阳性对照  
- 时限 ≤~1h；无实测留空；NaN/fill 禁令只写规格/构造（不进「复现技巧」）

**forbidden**

- NaN 强写 / token fill / 伪造症状放大器；改 canonical 当场景  
- 以 GSM8K/golden 当成功；用 soft-inv 刷分顶替 HARD  
- 在本 skill 展开十问定界（→ `investigation` / `ref-kv-dump`）  
- 半截旧跑冒充实测；把构造禁令写进案例「复现技巧」

**逻辑输入：** bug/PR 锚点, Origin 标签, 拓扑/模型, 时限  
**逻辑输出：** SPEC, overlay, 三层率, samples, HARD|就绪, keep-set 打包提示

**依赖：** 复现后定界可交 investigation / ref-kv；无强制上游 skill。

**术语：** **origin-faithful** 释义主页在本 skill（审计 #36）。

---

## 维护规则

| 变更 | 改谁 |
|------|------|
| 已有 detector 算法 / 推荐阈值 | `config-recommender`（+ 手册 03） |
| 新增已合入 detector | `config-recommender` + `detector-sweep` |
| report JSON schema | `analysis`（+ 必要时 recommender 字段说明） |
| anomaly 构造纪律 / origin-faithful | `build-anomaly-env` |
| 仅文档措辞、代码参数不变 | 只改手册，skill 可不改 |

脚本 CLI 变更 → 同步本目录（权威）→ 内部仓 `analysis/skill/` 镜像（见 06 README 同步命令）。
