# ⑥ Agent Skills（排障 / 分析）

面向 Cursor / Agent：按现象启用 detectors、抓现场、离线对账、有标杆时做 KV 定界。

> 本目录是 **手册仓内的 skill 副本**（与代码对齐后的可分发版）。  
> 职责契约：[SKILLS_METADATA.md](./SKILLS_METADATA.md)（v1.1）。  
> 离线脚本实现仓：[runtime-guard-test](https://github.com/djh95/runtime-guard-test)（`analysis/scripts/`）。  
> 产品实现：`vllm_ascend/observability/runtime_guard/`（[#16849](https://github.com/vllm-project/vllm-ascend/pull/16849) + [#18644](https://github.com/vllm-project/vllm-ascend/pull/18644)）。  
> 人读流程仍以 [02 问题定位](../02_problem_localization.md) 为准；skill 负责可执行编排。

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
| 默认全关 | `is_fully_off` 热路径旁路（#18644 / backport 的 #18450 Perf） |
| ≤0.30 backport | 见 [05](../05_v030_backport/README.md)；**不含** #18644 鲁棒修复集合 |

## 维护

- 产品 detector / 配置字段变更 → 同步改本目录 + [03_detectors](../03_detectors/README.md) + [SKILLS_METADATA.md](./SKILLS_METADATA.md)。  
- 脚本 CLI 变更 → 同步改本目录 + 回写 [runtime-guard-test](https://github.com/djh95/runtime-guard-test) 的 `analysis/skill/`（若仍维护）。
