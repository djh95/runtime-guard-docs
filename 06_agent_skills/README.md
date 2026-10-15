# ⑥ Agent Skills（排障 / 分析）

面向 Cursor / Agent：按现象启用 detectors、抓现场、离线对账、有标杆时做 KV 定界。

> 本目录是 **手册仓内的 skill 副本**（与代码对齐后的可分发版）。  
> 离线脚本实现仓：[runtime-guard-test](https://github.com/djh95/runtime-guard-test)（`analysis/scripts/`）。  
> 产品实现：`vllm_ascend/observability/runtime_guard/`（[#16849](https://github.com/vllm-project/vllm-ascend/pull/16849) + [#18644](https://github.com/vllm-project/vllm-ascend/pull/18644)）。  
> 人读流程仍以 [02 问题定位](../02_problem_localization.md) 为准；skill 负责可执行编排。

## Skills

| Skill | 文件 | 何时用 |
|-------|------|--------|
| `runtime-guard-investigation` | [investigation/SKILL.md](./investigation/SKILL.md) | 端到端：triage → 抓现场 → ref → Q1–Q5 定界 |
| `runtime-guard-detector-sweep` | [detector-sweep/SKILL.md](./detector-sweep/SKILL.md) | 未定类：临时多开已合入 detector |
| `runtime-guard-config-recommender` | [config-recommender/SKILL.md](./config-recommender/SKILL.md) | 按现象推荐 `runtime_config` / dump 配额 |
| `runtime-guard-analysis` | [analysis/SKILL.md](./analysis/SKILL.md) | 已有 report（±dump）后的离线对账 |
| `runtime-guard-ref-kv-dump` | [ref-kv-dump/SKILL.md](./ref-kv-dump/SKILL.md) | force-feed 抓 ref + 两表对比 |

## 脚本怎么跑

```bash
# 克隆脚本仓（或本地 runtime-guard-analysis / runtime-guard-test）
export RG_TEST=/path/to/runtime-guard-test
PYTHONPATH="$RG_TEST" python -m analysis.scripts.<name> --help
```

常用：`summarize_reports` / `correlate_incident` / `verify_request_kv` / `inspect_kv_dump` /  
`prepare_ref_inputs` / `request_from_report` / `locate_first_divergence` / `compare_kv_similarity` /  
`compare_per_layer` / `stitch_kv`。

## 与产品对齐的硬事实（2026-10）

| 项 | 现状 |
|----|------|
| 已合入 detector | `token_repeat` / `logits_finite` / `spec_acceptance` |
| **未合入**（勿启用） | `output_substring` / `token_logprob` / `slot_*` / `kv_state` |
| Runner | **仅 Model Runner v2** |
| 热更 | 启动参数 `runtime_config_hot_reload=true`（**不是** JSON 里的 `reload_interval_seconds`） |
| 停检 | `report.max_per_req`（**不是** `stop_after_alert`） |
| Dump | 仅 native `dump_kv`；无 msprobe |
| 默认全关 | static idle 热路径旁路（#18644 / backport 的 #18450 Perf） |
| ≤0.30 backport | 见 [05](../05_v030_backport/README.md)；**不含** #18644 鲁棒修复集合 |

## 维护

- 产品 detector / 配置字段变更 → 同步改本目录 + [03_detectors](../03_detectors/README.md)。  
- 脚本 CLI 变更 → 同步改本目录 + 回写 [runtime-guard-test](https://github.com/djh95/runtime-guard-test) 的 `analysis/skill/`（若仍维护）。
