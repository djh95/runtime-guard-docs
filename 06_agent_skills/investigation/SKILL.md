---
name: runtime-guard-investigation
description: >-
  Debug intermittent NPU/vllm-ascend precision bugs with runtime_guard:
  detect → report → dump_kv → force-feed report token ids for ref → compare
  and localize (KV vs model/post-sample; compute vs pollution; stage/token/
  layer/block). Native dump_kv only; no msprobe. Align with handbook 02 Q1–Q5.
---

# runtime_guard-Based Bug Investigation

Living doc：步骤/路径过时必须回写本文件。  
手册：[02 问题定位](../../02_problem_localization.md) · 启服：[01](../../01_enable_and_start.md) · 算法：[03](../../03_detectors/README.md)  
脚本仓：[runtime-guard-test](https://github.com/djh95/runtime-guard-test) · 产品：`vllm_ascend/observability/runtime_guard/`（[#16849](https://github.com/vllm-project/vllm-ascend/pull/16849)/[#18644](https://github.com/vllm-project/vllm-ascend/pull/18644)）

**Dump 只有 native `dump_kv`。** 禁止 msprobe / PrecisionDebugger / 自造 dumper。

```bash
export RG_TEST=/path/to/runtime-guard-test
alias rgpy='PYTHONPATH="$RG_TEST" python -m analysis.scripts'
```

## 磁盘卫生

测前 `df`；对比结束后删除服务产生的临时全量 `kv_cache`（dump 的 `.pt` 小样证据可留）。勿把全量 KV 提交进 git。

## 开场必问（4 输入）

1. **运行环境**：容器 / 路径 / `{MODE}` / `{MODEL}` / `{TOPO}` / 卡号  
2. **启动脚本** `{START}`  
3. **请求脚本** `{REPRO}`  
4. **谁跑服务**：skill `docker exec`，还是用户自起？确认前不要擅自起服。

| Var | 含义 |
|-----|------|
| `{CONTAINER}` `{WS}` `{SRC}` | 容器与源码树 |
| `{RG_CFG}` | live `runtime_config.json`（绝对路径） |
| `{REPORT}` / `{KV_ROOT}` | 报告根 / `kv_cache` 根 |
| `{MODE}` `{MODEL}` `{TOPO}` | graph/eager、权重、单进程或 PD |

## 目标（定界，非定位）

| 问题 | 典型结论 |
|------|----------|
| 哪一类 | KV / 模型计算 / 后采样 |
| 机制 | 计算错 vs KV 污染 |
| 时空 | prefill/decode、首坏 token、首坏层 |
| 粒度 | 单 token / 连续 / block |
| 时机 | 写入时即坏 vs 写入后污染 |

Phase E.1：buggy vs ref 首分歧。  
Phase E.2：KV 几乎一致 → 偏后采样/输出头之后（仍不用 msprobe）。

## 精度定界决策树 Q1–Q5（有 buggy+ref 时强制按序）

前置：命中 +（可选）dump；`verify_request_kv` PASS；force-feed 出 ref（见 `runtime-guard-ref-kv-dump`）。

| 问 | 怎么答 |
|----|--------|
| **Q1 KV 是否异常？** | 高相似无首分歧 → 非 KV；有首分歧 → Q2 |
| **Q2 阶段/token/层？** | prompt→prefill；output→decode；全层齐坏→整包写/传；从某层起→该层 |
| **Q3 粒度？** | 单 token / 连续 / `block_size` 级 |
| **Q4 异常点之后？** | 邻域恢复→写入后污染；一路坏→写入时即错 |
| **Q5 类型（cos）？** | 断崖→0≈污染；平台~0.8–0.9≈计算；nan/inf≈数值炸 |

**交付模板（定界，非定位）：**

```text
【定界】KV=<异常|正常|未知(无标杆)>; 阶段=<prefill|decode|未知>;
首坏token=<i/role|未知>; 首坏层=<L|未知>;
粒度=<单token|连续|block|未知>; 时机=<写入时即坏|写入后污染|未知>;
类型=<污染断崖|计算平台|后采样/非KV|仅detector类>;
标杆=<有|无>; 证据=<report路径 / dump路径 / 脚本>;
【非结论】未定位到具体算子或提交。
```

无清洁标杆：停在「问题类 + 可归档现场」；**不要伪造 ref**。

---

## Step 1 — Triage

**不适合（换工具）**

| 现象 | 原因 |
|------|------|
| Hang / 死锁 | Guard 依赖集体通信，**无法对 hang 做根因定界** |
| 启动 crash | 服务起来后才工作 |
| OOM / 泄漏 | 不监控内存 |
| 纯吞吐下降 | profiling |
| 权重/拓扑/传输栈错 | 先修配置；配错时 Guard 自身也不可靠 |

**适合**

- `token_repeat` / `logits_finite` / `spec_acceptance`（仅 MTP）  
- KV 可疑：`manual_dump` / `dump_kv` + 有标杆时 ref 对比  
- **勿启用**未合入：`output_substring`、`token_logprob`、`slot_*`

未定类 → `runtime-guard-detector-sweep`（临时三键，dump 先关）。

## Step 2 — 复现可行性

问复现率/条件/`{START}`/`{REPRO}`/谁跑。先短测 1–2h；起服前 `npu-smi`。起不来 → 不是 Guard 问题。

## Step 3 — 源码与安装

确认 `{SRC}` 含 `vllm_ascend/observability/runtime_guard/`（旧路径 `vllm_ascend/runtime_guard/` 已迁）。  
`pip show vllm-ascend` 与源码一致；需 MRV2。≤0.30 无 Guard 时先打手册 [05 patch](../../05_v030_backport/README.md)（**不含** #18644 鲁棒集合）。

## Step 4 — dump 管线冒烟

1. `runtime_config_hot_reload=true` 启动；dump 配额先 0。  
2. 热更：`auto_max_times>0` 或 `manual_dump` 水位；目标 detector `on_trigger` 含 `dump_kv`。  
3. Grep 确认 reload（失败保留旧配置）。  
4. 一笔请求 → report（last-PP TP0）+ `kv_cache/.../wave_*/<rank_tag>/*.pt`（各 TP）。  
5. `du` / `df` → `auto_max_times ≤ disk_free×0.7/per_req_size`（与 recommender 取小）。

| 现象 | 处置 |
|------|------|
| 无 report | detector enabled？是否 last-PP TP0？ |
| 有 report 无 kv | `on_trigger` / `auto_max_times` / cooldown |
| 只有 tp0 | 其它 last-PP TP 同波？ |
| 热更无效 | `runtime_config_hot_reload`；路径；拒绝日志 |

## Step 5 — 压测抓真命中

热更到压测态（recommender）：目标 detector ON；`report.max_per_req`；`auto_max_times`；`on_trigger: ["report","dump_kv"]`。  
先信 detector，再用输出反查；误报目录及时删。  
需 `save_sensitive_info: true` 才能 force-feed。

```bash
rgpy.summarize_reports --report-dir {REPORT} --limit 20
```

## Step 5.5 — 对账

```bash
rgpy.verify_request_kv --report {REPORT}/<type>/report_....json --report-dir {REPORT}
rgpy.correlate_incident --report-dir {REPORT} --req-id <req_id>
```

`PASS` 再抓 ref。

## Step 6 — 抓 ref

见 `runtime-guard-ref-kv-dump`：同模型/拓扑/**同 MODE**；token-id force-feed；仅 native dump。

## Step 7 — 首分歧（E.1）

```bash
rgpy.locate_first_divergence \
  --buggy-dir {KV_ROOT}/<type>/<bad>/wave_N/<rank_tag>/ \
  --ref-dir   {KV_ROOT}/<type>/<ref>/wave_N/<rank_tag>/ \
  --report {REPORT}/<type>/report_....json \
  --block-size 128 --cos-thresh 0.99

rgpy.compare_per_layer \
  --buggy-dir ... --ref-dir ... --report ...
```

强制填 Q1–Q5 模板。完成后删临时全量 `kv_cache`（保留小样证据）。

## Step 8 — KV 一致（E.2）

定界「非 KV」；结合 detector 类收口；**不上 msprobe**。

## dump_kv 速查

- 触发：`on_trigger` 含 `dump_kv`，或 manual 水位（需热更）  
- 配额：`auto_max_times` + `auto_cooldown_seconds`；与 active manual **互斥**  
- 无 `dump.enabled`  
- 布局：`{REPORT}/kv_cache/<type>/<req_id>/wave_N/<rank_tag>/*.pt`  
- 各 TP 同 live JSON  

## Related skills

`runtime-guard-detector-sweep` · `runtime-guard-config-recommender` · `runtime-guard-analysis` · `runtime-guard-ref-kv-dump`
