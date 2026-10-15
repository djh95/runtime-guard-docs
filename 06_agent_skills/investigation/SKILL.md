---
name: runtime-guard-investigation
description: >-
  Orchestrate end-to-end runtime_guard debugging: triage whether Guard fits,
  collect inputs, delegate to detector-sweep / config-recommender / analysis /
  ref-kv-dump, then deliver Q1–Q5 delimitation (not root-cause). Do not invent
  runtime_config thresholds or reimplement offline/ref scripts. Native dump_kv
  only; no msprobe. Align with handbook 02.
---

# runtime_guard investigation（编排总控）

**类型：编排。** 只做 triage、收集输入、委派原子 skill、汇总定界交付。  
底层配置 / 读盘 / force-feed / KV 对比 **委派**，不在本 skill 重写一遍。

手册：[02](../../02_problem_localization.md) · [01](../../01_enable_and_start.md) · [03](../../03_detectors/README.md)  
契约：[SKILLS_METADATA.md](../SKILLS_METADATA.md)  
脚本仓：[runtime-guard-test](https://github.com/djh95/runtime-guard-test)  
产品：`vllm_ascend/observability/runtime_guard/`（[#16849](https://github.com/vllm-project/vllm-ascend/pull/16849)/[#18644](https://github.com/vllm-project/vllm-ascend/pull/18644)）

**Dump 只有 native `dump_kv`。** 禁止 msprobe / PrecisionDebugger / 自造 dumper。

## 开场必问

1. **运行环境**：容器 / 路径 / `{MODE}` / `{MODEL}` / `{TOPO}` / 卡号  
2. **启动脚本** `{START}` · **请求脚本** `{REPRO}`  
3. **谁跑服务**（确认前不要擅自起服）  
4. **版本**、能否压测、有无清洁标杆、本地是否已有 `report`/`kv_cache`

| Var | 含义 |
|-----|------|
| `{RG_CFG}` | live `runtime_config.json`（绝对路径） |
| `{REPORT}` / `{KV_ROOT}` | 报告根 / `kv_cache` 根 |
| `{MODE}` `{MODEL}` `{TOPO}` | graph/eager、权重、拓扑 |

## Step 1 — Triage

**不适合（换工具，终止）**

| 现象 | 原因 |
|------|------|
| Hang / 死锁 | Guard 依赖集体通信，无法对 hang 做根因定界 |
| 启动 crash | 服务起来后才工作 |
| OOM / 泄漏 | 不监控内存 |
| 纯吞吐下降 | profiling |
| 权重 / 拓扑 / 传输栈错 | 先修配置 |

**适合：** `token_repeat` / `logits_finite` / `spec_acceptance`（MTP）；KV 可疑靠 dump+标杆。  
**勿启用未合入：** `output_substring` / `token_logprob` / `slot_*` / `kv_state`。

## Step 2 — 委派（禁止自创配置参数）

| 现状 | 调用 |
|------|------|
| 现象未定类 | `runtime-guard-detector-sweep` → 临时只 report |
| 现象已定类 / 要抓 dump | `runtime-guard-config-recommender`（`troubleshoot`） |
| 业务要恢复默认全关 | `config-recommender`（`business_default`） |
| 已有 report（±dump） | `runtime-guard-analysis` |
| analysis 得 verify=PASS 且可起清洁标杆 | `runtime-guard-ref-kv-dump` |

可**复述**下游给出的 JSON；**禁止**自己编造 window / 阈值 / `auto_max_times` / cooldown / `on_trigger`。

启服与热更细节见手册 01；源码路径须含 `observability/runtime_guard/`（MRV2）。≤0.30 无 Guard 时先看 [05](../../05_v030_backport/README.md)（**不含** #18644 鲁棒集合）。

## 目标（定界，非定位）

有 buggy+ref 时按序答 Q1–Q5（对比细节在 `ref-kv-dump`）：

| 问 | 要点 |
|----|------|
| Q1 KV 是否异常？ | 高相似无首分歧 → 非 KV |
| Q2 阶段/token/层？ | prefill vs decode；整包 vs 从某层起 |
| Q3 粒度？ | 单 token / 连续 / block |
| Q4 异常点之后？ | 恢复→写入后污染；一路坏→写入时即错 |
| Q5 类型（cos）？ | 断崖≈污染；平台≈计算；nan/inf≈数值炸 |

**交付模板：**

```text
【定界】KV=<异常|正常|未知(无标杆)>; 阶段=<prefill|decode|未知>;
首坏token=<i/role|未知>; 首坏层=<L|未知>;
粒度=<单token|连续|block|未知>; 时机=<写入时即坏|写入后污染|未知>;
类型=<污染断崖|计算平台|后采样/非KV|仅detector类>;
标杆=<有|无>; 证据=<report路径 / dump路径 / 脚本>;
【非结论】未定位到具体算子或提交。
```

无清洁标杆：停在「问题类 + 可归档现场」；**不要伪造 ref**。

## forbidden

- 在本 skill 内手写完整排障 JSON / 离线脚本流程 / force-feed  
- 承诺定位算子、内核或具体 commit  
- 从本流程跳过 `verify_request_kv` 直接宣称可做层定界

## Related

`detector-sweep` · `config-recommender` · `analysis` · `ref-kv-dump` · [SKILLS_METADATA.md](../SKILLS_METADATA.md)
