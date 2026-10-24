# ② 问题定位分析（能力、流程、定界边界）

本文回答三件事：

1. Runtime Guard **整体是什么、能解决哪类问题**  
2. **如何操作**（从启检测到初步定界）  
3. **定界到哪一步为止**——什么叫「能定界、无法定位」

案例模版见 [04_case_studies](../04_case_studies/README.md)（15 典型 keep-set），不堵本流程。

## 上游文档

| 说明 | URL |
|------|-----|
| 功能说明 | https://github.com/vllm-project/vllm-ascend/blob/main/docs/source/user_guide/feature_guide/runtime_guard.md |
| runtime_config | https://github.com/vllm-project/vllm-ascend/blob/main/docs/source/user_guide/configuration/runtime_config.md |
| 检测实现目录 | https://github.com/vllm-project/vllm-ascend/tree/main/vllm_ascend/observability/runtime_guard/detector |
| 控制面 PR | https://github.com/vllm-project/vllm-ascend/pull/16849 |
| 性能与鲁棒增强 PR | https://github.com/vllm-project/vllm-ascend/pull/18644 |

---

## 1. 整体功能（给一线的一张图）

```text
在线信号 ──► Detector 命中 ──► report JSON（坐标/类型）
                │
                └─(+ dump_kv)──► 本请求 KV block 快照 .pt
                                      │
                    ┌─────────────────┴─────────────────┐
                    │ 有清洁标杆 + 同 token force-feed*  │
                    ▼                                   ▼
              buggy vs ref 首分歧              仅有报告/单侧 dump
              → 阶段/token/层 定界              → 类与现场，难到层
```

| 模块 | 作用 |
|------|------|
| Detector | 检测异常包括：`token_repeat`（复读/卡词）、`logits_finite`（采样前 NaN/Inf）、`spec_acceptance`（Spec 接受率/长度异常）等，写成可检索 report 事件 |
| Report | 结构化现场（类型、req、token 窗口等） |
| `dump_kv` | 落 **本请求** 相关 KV block（last-PP×TP）；不是全 cache、不是 op 级 dump |
| 离线对比（有标杆时） | 首坏 token / 首坏层级 **定界**；不自动指出是哪行代码 / 哪个算子 bug |

**一句话：** Guard 是 **观测 + 抓现场 +（有条件时）定界** 工具，不是自动根因定位器。

\* **force-feed**：按报告里的 token id 原样喂给干净服务（禁止再 tokenize 字符串）。

---

## 2. 能解决什么问题？

### 2.1 适合（Guard 主战场）

| 现象 | 典型入口 | 说明 |
|------|----------|------|
| 输出复读 / 局部卡词 | `token_repeat` | 最轻；适合先开 |
| 采样前 NaN/Inf、突然乱码伴数值炸 | `logits_finite` | 给「数值是否已坏」的强信号；**命中后仍先 `dump_kv`**（有效槽有限/Inf；未用槽分级：有限非 0≈卫生，Inf/NaN≈可影响结果）；skill **`msprobe-dump`** 殿后（statistics · eager · 禁图） |
| Spec 接受率/长度异常 | `spec_acceptance` | 需 MTP/Eagle 等 speculative |
| 怀疑 KV / PD 传写出问题 | `dump_kv` +（有标杆时）对比 | 适用于有限异常 / `token_repeat` 等；detector 给坐标，定界靠对比 |
| **偶发、难复现** | 热更 + report/dump | 命中即抓，不必先有稳定复现脚本 |

### 2.2 不适合（直接换工具）

| 现象 | 原因 |
|------|------|
| Hang / 死锁 | Guard 自身依赖集体通信，无法对 hang / 死锁做根因定界 |
| 启动 crash / import | 服务起来之后才工作 |
| OOM / 显存泄漏 | 不监控内存 |
| 纯吞吐下降 | profiling / bench |
| 权重 / checkpoint 错 | 不读权重 |
| TP/PP/DP 配错、传输栈坏 | 先修拓扑；配错时 Guard 自身也不可靠 |

### 2.3 特殊场景：**必现问题，但拿不到标杆数据**

> 先确认真是必现：见 §4 Step 0.5（连测 / 换输入 / 消融 / PD 单边）。未验证前不要直接按本节收束。

一线常见卡点：问题 **已验证必现**，却 **没有清洁对照环境**（无法起一份「确认正确」的同模型同拓扑服务，或无法 force-feed 同一 token 序列）。

无标杆时仍可：开 detector 确认异常类、落 report、可选单侧 `dump_kv` 供事后对比、用报告 token ids 作以后标杆输入。  
无标杆时不能：做 buggy vs ref 的 KV 首分歧，或可靠回答「从哪一层开始坏」。单侧 `.pt` 不能单独证明是写坏还是算坏。

**结论：** 无标杆时，Guard 的交付停在 **「问题类 + 可归档现场」**；这是合格的 **初步定界**，不是根因定位。标杆就绪后再走 §4 Step 6–8。

---

## 3. 能定界到什么程度？「定界」vs「定位」

| 层级 | 含义 | Guard 是否覆盖 |
|------|------|----------------|
| **发现** | 知道发生了异常类事件 | ✅ detector + report |
| **定界（粗）** | 限定到某 req、某类、某段输出 / 是否非有限 logits | ✅ |
| **定界（细）** | 限定到 prefill/decode、首坏 token、首坏层、污染 vs 计算平台 | ✅ **仅当** 有对账通过的 buggy+ref dump |
| **定位** | 指到具体算子、kernel、某次提交、某条分支 | ❌ **不在范围**；需调试器 / 单测 / code review |

细定界按下方 **§5 十问检查单** 填 outcome；「已定界」≠「已定位到根因」。

---

## 4. 推荐流程（初步定界）

```text
症状 triage →（看似必现则先验复现）→ 启 Guard → 冒烟(report±dump) → 压测抓命中
  → 对账 → [有标杆] force-feed 抓 ref → 首分歧 → §5 十问
         → [无标杆] 停在「类 + 现场」，记入案例待补标杆
```

### Step 0 — Triage

按 §2 判断是否适合；不适合则明确停。若业务侧声称「必现 / 一请求就坏」，先做下面 **§4.0**，再按 §2.3 走无标杆停点或继续开 Guard。

### Step 0.5 — 看似必现：先验证再定论

「看起来每次都坏」≠ 已证实必现。进 dump / 定界前用下面四步压一压，避免把偶发或配置敏感问题写成必现。

| # | 动作 | 怎么判断（outcome） |
|---|------|----------------------|
| 1 | **连测多次** | 同一请求 / 同批脚本至少跑 **≥3 轮**；记录成功/失败比。一轮坏、一轮好 → 记偶发，走热更抓现场。 |
| 2 | **换输入与长度** | 短输出（如 `max_tokens=1`）常打不出复读类。换多条 prompt、把 `max_tokens` 提到业务长度（如 32–128+）再试；仍稳定坏 → 倾向必现。 |
| 3 | **消融** | 关掉可疑特性（graph / APC / speculative·MTP / 某量化路径 / 自定义采样等）后是否恢复。关了就好 → 「与 X 相关」；关了仍坏 → 更像底座路径。 |
| 4 | **PD 解耦专项** | P–D 分离部署时再测 **单 P**、**单 D**。单边健康、合部才坏 → 优先传写/交接；单边也坏 → 先修该边。 |

交接写事实句，例如：`复现 5/5；max_tokens=1 不复现、=64 复现；关 MTP 后恢复；单 P/单 D 正常、PD 合部失败`。

### Step 1 — 启服与配置

见 [01_enable_and_start/README.md](../01_enable_and_start/README.md)。排障期建议 `runtime_config_hot_reload=true` + 绝对路径。

### Step 2 — Dump 管线冒烟（再压测）

1. 先 `auto_max_times: 0`，只 `report`，确认 JSON 写出。  
2. 再开 `dump_kv` + 合理 `auto_max_times`（按磁盘空间粗估：`auto_max_times ≈ 磁盘剩余空间×0.7 / per_req_size`，其中 `per_req_size` 为单请求 KV 快照预估大小）。  
3. 确认 last-PP 各 `tp*` 的 `.pt` 齐全。

### Step 3 — 压测抓真命中

- 有多份 report / sample 时：**优先查看看起来就错误的**（乱码 / 异常样本）。  
- `report.save_sensitive_info: true` 才能把 token ids 留给后续 force-feed。  
- 误报目录及时清理腾盘。

### Step 4 — 对账（本仓离线脚本）

离线脚本在本仓 [06_agent_skills/scripts/](../06_agent_skills/scripts/)（与 [06 Agent Skills](../06_agent_skills/README.md) 同入口）：

```bash
export RG_DOCS=/path/to/runtime-guard-docs
SCRIPTS="$RG_DOCS/06_agent_skills/scripts"
python "$SCRIPTS/summarize_reports.py" --report-dir {REPORT}
python "$SCRIPTS/verify_request_kv.py" --report ... --kv-dir {KV_RANK_DIR}
```

`verify_request_kv` **PASS**（脚本验 dump，非案例结案档）再抓标杆；**FAIL** 先修路径 / 配额 / `on_trigger`。

### Step 5 — 有标杆：同 token 序列抓 ref

- 同模型、同拓扑、**同 MODE**（勿用 eager↔graph 当对照）。  
- 用 report 的 `prompt_token_ids` + `output_token_ids` **force-feed**（token-id API），禁止字符串重 tokenize。  
- Guard KV 对比只用 native `dump_kv`（不要 msprobe / 临时自造 dumper **冒充** KV 对比源）。`logits_finite` 已命中时 **不做** KV 对账，改走 msprobe 算子 I/O。

### Step 6 — 首分歧与十问检查单

见 §5。完成后删除服务运行产生的临时全量 `kv_cache`（dump 输出的 `.pt` 小样证据保留即可）。

> 对比异常侧与清洁标杆时，先找**第一个已出 KV 问题**的 token/层（数值不对，或余弦明显偏低）。下面的检查单现为 **十问**（Q1–Q10）；旧文若写 Q1–Q5，含义已并入此表。

### 无标杆时的停点

完成 Step 3（+ 可选单侧 dump）→ 标杆记「无」→ 转开发或等对照环境。不要伪造 ref。

---

## 5. KV 定界十问检查单（有 buggy+ref 时按序）

**前置：** `verify_request_kv` 脚本验 dump 通过；已有 buggy / ref dump。按序答下表，只填 **检查 outcome**。（此处 PASS 指脚本验，不是案例结案四档。）

| 问 | 检查什么（判断 outcome） |
|----|--------------------------|
| **Q1** | KV 是否异常？（高相似无首分歧 → 非 KV，停） |
| **Q2** | 首个不一致在 **prompt 还是 output**？索引大概在哪？ |
| **Q3** | 层：全层齐坏，还是 **从某层起坏**？ |
| **Q4** | 粒度：单 token / 连续 / 是否按 **`block_size`** 对齐？ |
| **Q5** | 首分歧之后 **是否恢复**（邻域 ~1 vs 一路坏）？ |
| **Q6** | **output 首 token 余弦**是否已明显偏低？（无 output 答未知） |
| **Q7** | cos **形态**：断崖→0 / 平台 ~0.8–0.9 / nan·inf？ |
| **Q8** | 是否 **仅 PD** 复现？单 P、单 D 各如何？（非 PD 答不适用/未测） |
| **Q9** | **和哪些特性相关 / 不相关**？（已做消融的：PD、TP/PP、长度/batch、dense vs hybrid 等——只写结果） |
| **Q10** | **对照是否完整可用**？（对比窗是否含 output；last-PP 各 TP 分片是否齐；buggy/ref 是否同 MODE/同拓扑） |

案例定界节见 [04](../04_case_studies/README.md)；agent 写作纪律与交付模板见 [investigation skill](../06_agent_skills/investigation/SKILL.md)。

---

## 6. 运维排障速查

| 现象 | 检查 |
|------|------|
| 无 report | detector `enabled`；是否 last-PP TP0 |
| 有 report 无 kv | `on_trigger` 含 `dump_kv`；`auto_max_times`；cooldown |
| 只有 tp0 | 其它 last-PP TP 是否同波；日志 `[runtime_guard dump_kv]` |
| 无更早 PP 层 | **预期**（不 dump 非 last PP） |
| 热更无效 | `runtime_config_hot_reload`；路径；reload 拒绝日志 |
| Manual 不触发 | 是否有 scheduled tokens；本进程「已拍次数」是否已 ≥ 目标总次数 `N`（内部常叫 `done`） |

日志关键字：`[runtime_guard sync]` / `manual_trigger` / `dump_kv` / `action`。

---

## 7. 硬约束

1. 不用换 eager/graph 当对照。  
2. 只用 native `dump_kv` 做 Guard 语义下的 KV 对比源。  
3. `.pt` 在 CPU `map_location` 上 load，勿占 NPU。

---

## 8. 相关手册页

- 启动：[01_enable_and_start/README.md](../01_enable_and_start/README.md)  
- 算法：[03_detectors/README.md](../03_detectors/README.md)  
- 实例：[04_case_studies/README.md](../04_case_studies/README.md)  
- `releases/v0.30.0` 发布线 patch：[05_v030_backport/README.md](../05_v030_backport/README.md)
