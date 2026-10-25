# ⑥ Agent Skills（排障 / 分析）

面向 Cursor / Agent：按现象启用 detectors、抓现场、离线对账、有标杆时做 KV 定界。

> **权威：** 本目录 `runtime-guard-docs/06_agent_skills/`（含 [SKILLS_METADATA.md](./SKILLS_METADATA.md) **v5.20.12**）。  
> **离线脚本：** [scripts/](./scripts/)（本仓）。  
> 产品实现：`vllm_ascend/observability/runtime_guard/`（[#16849](https://github.com/vllm-project/vllm-ascend/pull/16849) + [#18644](https://github.com/vllm-project/vllm-ascend/pull/18644)）。  
> 人读流程仍以 [02 问题定位](../02_problem_localization/README.md) 为准；skill 负责可执行编排。  
> **用户面短词汇表：** [04 · 词汇表](../04_case_studies/词汇表.md)（对账、有效槽、结案四档、钉点同跑、叠打等）。其它说法在出现处写白话，勿堆词典。

## 无满量评测矩阵时

公开路径：本目录 skill 契约 + [scripts/](./scripts/) + 手册 01–05 + `04` 的 `cases/Sxx/` 完整包。完整评测矩阵不在本仓。

| 仍可做 | 须停止 / 跳过 |
|--------|----------------|
| 读 METADATA / 各 skill README；用巡检（detector-sweep）/ recommender 产出配置 | 勿假设能拿到满量失败证据包 / runs |
| 跑本仓 `06_agent_skills/scripts/*.py`；人工读 `report_*.json` | 勿宣称未跑的 verify/ref 已完成 |
| 按 02 无标杆停点交接 | 满量分析矩阵 —— 内部可选 |

## Skills

| Skill | 类型 | 何时用 |
|-------|------|--------|
| `runtime-guard-investigation` | 编排 | 端到端：triage → 委派原子 skill → 十问定界交付 |
| `runtime-guard-detector-sweep` | 原子 · 在线 | 未定类巡检：临时开已合入 detector，只 report（极简模板） |
| `runtime-guard-config-recommender` | 原子 · 在线 | **正式配置唯一来源**（排障 / 业务默认） |
| `runtime-guard-analysis` | 原子 · 离线 | 已有 report（±dump）：汇总 / 关联 / verify / inspect |
| `runtime-guard-ref-kv-dump` | 原子 · 离线+启动服务 | verify PASS 后 force-feed（按报告 token id 原样喂干净服务）抓 ref + 两表对比 |
| `runtime-guard-msprobe-dump` | 原子 · 算子 dump | `logits_finite` 后放最后做：**statistics** + **eager only**（禁用 graph）；扫 `dump.json` 找首坏算子 |
| `build-anomaly-env` | 构造 · 评测基建 | 忠于原 bug 逻辑打故障补丁：从修复 PR 反推场景 → 合法旋钮抬复现率 → 三层计数 → 打包 |
| `apply-mrv1-patch` | 运维 · 适配补丁 | 多 release × **MRV1**（Model Runner v1）Guard → [`05_mrv1_backport`](../05_mrv1_backport/) |
| `apply-v030-mrv2-patch` | 运维 · 适配补丁 | **v0.30 × MRV2**（Model Runner v2）Guard → [`05_v030_backport`](../05_v030_backport/) |

**隔离：** 在线配置 skill 不做读盘；离线 skill 不输出 `runtime_config`。  
**门闩：** `ref-kv-dump` 前须 `verify_request_kv` PASS（脚本确认异常 dump 可读齐全，**不是**结案「KV 一致」）。  
原子 skill 可独立调用；勿从原子 skill 反调 investigation。

## 脚本怎么跑（本仓）

入口见 [scripts/README.md](./scripts/README.md)：

```bash
export RG_DOCS=/path/to/runtime-guard-docs
SCRIPTS="$RG_DOCS/06_agent_skills/scripts"
python "$SCRIPTS/summarize_reports.py" --help
```

常用：`summarize_reports` / `correlate_incident` / `verify_request_kv` / `inspect_kv_dump` /  
`score_completion_samples`（无 report 时评输出是否异常 / 是否漏检）/  
`prepare_ref_inputs` / `request_from_report` / `locate_first_divergence` / `compare_kv_similarity` /  
`compare_per_layer` / `stitch_kv`。

Anomaly 对外对照：本仓 `04_case_studies/cases/Sxx/evidence/`。契约见 [SKILLS_METADATA.md](./SKILLS_METADATA.md)（**v5.20.12**）。构造纪律见 [`build-anomaly-env`](./build-anomaly-env/SKILL.md)。用户面短词汇表见 [04 · 词汇表](../04_case_studies/词汇表.md)。  
结案分四档；整包证据必须同一轮跑批、同一次请求（见词汇表「钉点同跑」）；细节见 [`investigation`](./investigation/SKILL.md) 与 [`ref-kv-dump`](./ref-kv-dump/SKILL.md)。  
KV：问题必现但检测器没报告时可用 **`manual_dump`**。对比三步：先核对形状并屏蔽未用槽 → 再先报有效槽数值问题（写清子类型）→ 最后算相似度并填表、写**【事实总结】**。无标杆时也可先做单侧有效槽数值问题。  
**`logits_finite` 命中 → 仍先 [`ref-kv-dump`](./ref-kv-dump/SKILL.md)**（数值问题 + 未用槽分级 + 可算时余弦；短输出不跳过 KV）；**[`msprobe-dump`](./msprobe-dump/SKILL.md) 放最后做**（statistics · eager · 禁用 graph）：见 [`investigation`](./investigation/SKILL.md)。

## 与产品对齐的硬事实（2026-10）

| 项 | 现状 |
|----|------|
| 已合入 detector | `token_repeat` / `logits_finite` / `spec_acceptance` |
| **未合入**（勿启用） | `output_substring` / `token_logprob` / `slot_*` / `kv_state` |
| Runner | 产品 main / `05_v030`：**MRV2**；历史 release 接线：`05_mrv1` → **MRV1** |
| 热更 | 启动参数 `runtime_config_hot_reload=true`（**不是** JSON 里的 `reload_interval_seconds`） |
| 停检 | `report.max_per_req`（**不是** `stop_after_alert`） |
| Dump（Guard KV） | 对比源仅 native `dump_kv`（勿用 msprobe 冒充 KV） |
| `logits_finite` 后 | **仍先 KV**（有效槽：有限数 **或** 数值问题 Inf/NaN/全零…；未用槽有限非 0≈卫生，Inf/NaN≈可影响结果）→ **`msprobe-dump` 放最后做** |
| 默认全关 | **全关旁路**（static idle：detector/dump/热更全关；代码侧 `needs_sample_phase_hooks()` 为假时跳过 sample 壳） |
| `releases/v0.30.0` MRV2 backport | 见 [05_v030](../05_v030_backport/README.md)（skill `apply-v030-mrv2-patch`；`v0.30-rg.3` SOURCE `#18450` @ `96046a3f0`，**含** #18644 对齐） |
| 多 release MRV1 backport | 见 [05_mrv1](../05_mrv1_backport/README.md)（skill `apply-mrv1-patch`）；含 v0.30 MRV1，与 05_v030 互斥 |

## 维护

- 产品 detector / 配置字段变更 → 同步改本目录 + [03_detectors](../03_detectors/README.md) + [SKILLS_METADATA.md](./SKILLS_METADATA.md)。  
- 脚本 CLI 变更 → 先改本目录（权威）；镜像回写见 `_internal/MAINTAINER_SYNC.md`（非对外导航）。
