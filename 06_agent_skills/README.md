# ⑥ Agent Skills（排障 / 分析）

面向 Cursor / Agent：按现象启用 detectors、抓现场、离线对账、有标杆时做 KV 定界。

> 本目录是 **手册仓内的 skill 副本**（与代码对齐后的可分发版）。  
> 职责契约：[SKILLS_METADATA.md](./SKILLS_METADATA.md)（**v5.8**）。  
> 离线脚本实现仓：**内部** `runtime-guard-test`（需权限；`analysis/scripts/`）。  
> 产品实现：`vllm_ascend/observability/runtime_guard/`（[#16849](https://github.com/vllm-project/vllm-ascend/pull/16849) + [#18644](https://github.com/vllm-project/vllm-ascend/pull/18644)）。  
> 人读流程仍以 [02 问题定位](https://github.com/djh95/runtime-guard-docs/blob/main/02_problem_localization/README.md) 为准；skill 负责可执行编排。

## Skills

| Skill | 类型 | 何时用 |
|-------|------|--------|
| `runtime-guard-investigation` | 编排 | 端到端：triage → 委派原子 skill → Q1–Q5 定界交付 |
| `runtime-guard-detector-sweep` | 原子 · 在线 | 未定类：临时三键只 report（极简模板） |
| `runtime-guard-config-recommender` | 原子 · 在线 | **正式配置唯一来源**（排障 / 业务默认） |
| `runtime-guard-analysis` | 原子 · 离线 | 已有 report（±dump）：汇总 / 关联 / verify / inspect |
| `runtime-guard-ref-kv-dump` | 原子 · 离线+起服 | verify PASS 后 force-feed 抓 ref + 两表对比 |

**隔离：** 在线配置 skill 不做读盘；离线 skill 不输出 `runtime_config`。  
**门闩：** `ref-kv-dump` 前必须 `verify_request_kv` PASS。  
原子 skill 可独立调用；勿从原子 skill 反调 investigation。

## 脚本怎么跑

```bash
# 内部仓 runtime-guard-test（需权限 clone；不要用未授权的公开 HTTPS 当外链）
export RG_TEST=/path/to/runtime-guard-test
PYTHONPATH="$RG_TEST" python -m analysis.scripts.<name> --help
```

常用：`summarize_reports` / `correlate_incident` / `verify_request_kv` / `inspect_kv_dump` /  
`score_completion_samples`（无 report 的 precision/GAP）/  
`prepare_ref_inputs` / `request_from_report` / `locate_first_divergence` / `compare_kv_similarity` /  
`compare_per_layer` / `stitch_kv`。

Anomaly 定界：先读 `tests/build-anomaly-env/fail-evidence/Sxx/` 与三层率；契约见 [SKILLS_METADATA.md](./SKILLS_METADATA.md)（**v5.8**）。

**给其他 Agent 的离线复核包（15 典型 keep-set）：** [VERIFY_HANDOFF.md](./VERIFY_HANDOFF.md)。

## 与产品对齐的硬事实（2026-10）

| 项 | 现状 |
|----|------|
| 已合入 detector | `token_repeat` / `logits_finite` / `spec_acceptance` |
| **未合入**（勿启用） | `output_substring` / `token_logprob` / `slot_*` / `kv_state` |
| Runner | **仅 Model Runner v2** |
| 热更 | 启动参数 `runtime_config_hot_reload=true`（**不是** JSON 里的 `reload_interval_seconds`） |
| 停检 | `report.max_per_req`（**不是** `stop_after_alert`） |
| Dump | 仅 native `dump_kv`；无 msprobe |
| 默认全关 | **全关旁路**（static idle：detector/dump/热更全关；代码侧 `needs_sample_phase_hooks()` 为假时跳过 sample 壳） |
| `releases/v0.30.0` backport | 见 [05](https://github.com/djh95/runtime-guard-docs/blob/main/05_v030_backport/README.md)（BASE 见 CHANGELOG）；含 #18450 Perf idle；**不含** main #18644 鲁棒修复集合 |

## 权威与同步

- **公开权威：** 本目录 `runtime-guard-docs/06_agent_skills/`（含 [SKILLS_METADATA.md](./SKILLS_METADATA.md) **v5.8**）。  
- **工作镜像：** 内部仓 `runtime-guard-test/analysis/skill/`（可能短暂滞后；勿假设 bit-identical）。  
- 回写镜像（有权限时）：

```bash
export RG_DOCS=/path/to/runtime-guard-docs
export RG_TEST=/path/to/runtime-guard-test
rsync -a --delete   --exclude VERIFY_HANDOFF.md   "$RG_DOCS/06_agent_skills/" "$RG_TEST/analysis/skill/"
# VERIFY_HANDOFF 仅手册仓保留亦可；需要时单独 cp
```

## 维护

- 产品 detector / 配置字段变更 → 同步改本目录 + [03_detectors](https://github.com/djh95/runtime-guard-docs/blob/main/03_detectors/README.md) + [SKILLS_METADATA.md](./SKILLS_METADATA.md)。  
- 脚本 CLI 变更 → 先改本目录（权威），再按上节 rsync 回写内部仓 `analysis/skill/`。
