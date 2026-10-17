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

手册：[02](https://github.com/djh95/runtime-guard-docs/blob/main/02_problem_localization.md) · [01](https://github.com/djh95/runtime-guard-docs/blob/main/01_enable_and_start.md) · [03](https://github.com/djh95/runtime-guard-docs/blob/main/03_detectors/README.md)  
契约：[SKILLS_METADATA.md](./SKILLS_METADATA.md)  
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

### 三层率（anomaly / 压测必记）

| Layer | 含义 | 证据 |
|-------|------|------|
| **trigger** | overlay / 故障路径真正打到 | `ANOMALY_TRIGGER` 计数、overlay 日志 |
| **precision** | 输出/数值已坏（可无 report） | samples 垃圾文、temp=0 发散、`score_completion_samples` |
| **detect** | 已合入 detector 出 report | `report/<type>/report_*.json` 计数 |

**trigger ≠ precision ≠ detect。** 有 trigger+precision 但 detect=0 → **FAIL+GAP**（记缺口，勿造 NaN/填 token 伪装 PASS）。

### 根因 class → 已合入 detector（来自 easy wave）

| Class（示例 Sxx） | 典型症状 | 主 detector | 备注 |
|------------------|----------|-------------|------|
| MoE 路由/合成/renorm（S06,S16–S19） | 复读、digit/`***`/`ctx` echo、ZWSP | `token_repeat` | 无 MoE 专用 detector |
| KV recycle / packed stride / slot→0（S08,S10′,S12） | 复读、xxxx collapse | `token_repeat` | KV 类；verify+ref 可定界 |
| MLA pad / o_proj empty（S11,S14） | digit/junk、graph pad | `token_repeat` | 间接 KV；dump 路径常有 |
| FIA FULL-graph pad（S32，soft-inv #7144） | **unique** pad-echo（`wN_M…` / `_0_0_0`）；identical-mode 低估 | **`token_repeat`** | **L2**（graph pad keep descriptor）；≠ S14 o_proj empty；score=`pad_echo` |
| Incomplete softcap（S33，÷cap+tanh skip *cap） | digit/`1.1.1…` 复读 | **`token_repeat`** | **L2**（softcap incomplete）；≠ S20 unstable/overflow（`!!!!`/token0） |
| Attn scale drop（S34，1/sqrt(d)→1.0） | unique digit/junk 混杂；identical-mode 低估 | **`token_repeat`** | **L2**（wrong attn temperature）；≠ S20/S32/S33 |
| Causal-off / future leak（S35，causal=False + mask=None） | 强 `phrase_repeat` / prompt-echo 复读 | **`token_repeat`** | **L2**（non-causal / sparse_mode=0）；≠ S34 scale |
| RoPE 第二半写丢（S25，soft-inv #7082） | digit/`1.1.1…` 复读塌缩 | **`token_repeat`** | **L2 class-hint**（RoPE half）；≠ S11 pad；勿宣称定位到 Triton store 行 |
| RMSNorm fp32 weight-mul（S26，soft-inv #42379） | 同上类复读；dtype/cast | **`token_repeat`** | **L2**（norm dtype）；与 S25 症状可重叠，靠 overlay/场景区分 |
| RoPE neox→interleaved 风格错（S28，#7341/#7082 class） | 句/短语级复读（score=`phrase_repeat`） | **`token_repeat`** | **L2**；≠ S25 half-drop ≠ S11；samples 可能看似「正常英文」 |
| Softcap / 不稳定 softmax 数值溢出（S20，constructed） | 全请求 `!!!!…` / token0 塌缩；temp≪1 放大 | **`token_repeat` 为主**；兼开 `logits_finite` | Inf/NaN 可能在采样内被吃掉 → 未必亮 `logits_finite`；MRV2 须打 **V2 Sampler**（非仅 AscendTopKTopPSampler） |
| Logits fp16 demote（S29，sampling/cast） | digit/`1.1.1…` 复读；低 temp 放大 | **`token_repeat`** | **L2**（cast）；≠ S20 softcap ≠ S26 RMSNorm mul；打 **V2 Sampler** |
| Null-block KV dirt（S30，soft-inv #39444） | 复读塌缩；block0 脏 | **`token_repeat`** | **L2**（+可选 L3 KV）；≠ S01 skip-zero ≠ S10 recycle ≠ S23/S24 |
| Residual stream drop（S31） | 强 identical 短语复读（如 `FieldType`×N） | **`token_repeat`** | **L2**（add-rms 丢 residual）；≠ S26（fp32-mul 仍 accumulate） |
| Spec residual resample RNG 无 SALT（S22，#18657） | 接受率异常偏低（如 0–0.27）；文本可看似正常 | **`spec_acceptance` 为主**；辅 `token_repeat` | ≠ S05（NaN argmax）；≠ S20；需 MTP/eagle3 + `temperature>0`；precision 常为 **分布性**（勿只靠 samples 垃圾启发式） |
| 权重腐蚀 always-on（S23，constructed） | 启动后恒定复读/塌缩 | **`token_repeat`** | **仅 L1 detect**；禁止宣称哪一层/哪个 weight；负对照=干净 ckpt |
| 量化 scale always-on（S24，constructed） | W8A8 启动后恒定 `token_repeat` | **`token_repeat`** | **仅 L1**；≠ S07（路径触发+GAP）；**不能**指出哪条 scale |
| 有限垃圾 / 跨请求全同（S01,S07） | mixed-script、48/48 identical | **当前均弱** | **GAP**：见 `DETECTOR_GAPS.md`；S24 能 detect 时勿与 S07 混谈 |
| NaN/Inf 数值炸（logits 仍可见） | non-finite logits | `logits_finite` | 有限垃圾 **不会** 命中；与 S20 塌缩路径区分 |

有限垃圾 / identical-across-requests：**不要**宣称「未复现」；归档 samples + `score_completion_samples`，标 **GAP**，等未来 garbled / cross-req detector。

## Step 2 — 委派（禁止自创配置参数）

| 现状 | 调用 |
|------|------|
| 现象未定类 | `runtime-guard-detector-sweep` → 临时只 report |
| 现象已定类 / 要抓 dump | `runtime-guard-config-recommender`（`troubleshoot`） |
| 业务要恢复默认全关 | `config-recommender`（`business_default`） |
| 已有 report（±dump） | `runtime-guard-analysis` |
| report 空但有 completion samples / FAIL+GAP | `analysis` → `score_completion_samples`（勿 skip） |
| analysis 得 verify=PASS 且可起清洁标杆 | `runtime-guard-ref-kv-dump` |

可**复述**下游给出的 JSON；**禁止**自己编造 window / 阈值 / `auto_max_times` / cooldown / `on_trigger`。

启服与热更细节见手册 01；源码路径须含 `observability/runtime_guard/`（MRV2）。≤0.30 无 Guard 时先看 [05](https://github.com/djh95/runtime-guard-docs/blob/main/05_v030_backport/README.md)（**不含** #18644 鲁棒集合）。

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

`detector-sweep` · `config-recommender` · `analysis` · `ref-kv-dump` · [SKILLS_METADATA.md](./SKILLS_METADATA.md)
