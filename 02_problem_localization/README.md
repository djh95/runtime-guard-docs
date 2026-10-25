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
                    （单侧也可先检「数值问题」：有效/未用分写；不必先有标杆）
                                      │
                    ┌─────────────────┴─────────────────┐
                    │ 有清洁标杆 + 同 token force-feed*  │
                    ▼                                   ▼
              buggy vs ref 首分歧              仅有报告/单侧 dump
              → 阶段/token/层 定界              → 类 + 现场 + 单侧数值结论
```

| 模块 | 作用 |
|------|------|
| Detector | 检测异常包括：`token_repeat`（复读/卡词）、`logits_finite`（采样前 NaN/Inf）、`spec_acceptance`（Spec 接受率/长度异常）等，写成可检索 report 事件 |
| Report | 结构化现场（类型、req、token 窗口等） |
| `dump_kv` | 落 **本请求** 相关 KV block（last-PP×TP）；不是全 cache、不是 op 级 dump |
| 单侧数值检查 | **无标杆也可做**：对异常 dump 的有效槽查数值问题（全零 / 有限非零 / NaN·Inf·范数零）；未用槽另记（见 skills v5.20.10+） |
| 离线对比（有标杆时） | 首坏 token / 首坏层级 **定界**；不自动指出是哪行代码 / 哪个算子 bug |

**一句话：** Guard 是 **观测 + 抓现场 +（有条件时）定界** 工具，不是自动根因定位器。

\* **force-feed**：按报告里的 token id 原样喂给干净服务（禁止再 tokenize 字符串）。

---

## 2. 能解决什么问题？

### 2.1 适合（Guard 主战场）

| 现象 | 典型入口 | 说明 |
|------|----------|------|
| 输出复读 / 局部卡词 | `token_repeat` | 最轻；适合先开 |
| 采样前 NaN/Inf、突然乱码伴数值炸 | `logits_finite` | 给「数值是否已坏」的强信号；**命中后仍要做 KV**：先 `dump_kv`，再对有效槽查数值问题（全零 / 有限非零 / NaN·Inf·范数零），未用槽另记（0 / 有限非零≈卫生，NaN·Inf≈可影响结果）。生成很短时，**层定位会变弱**，但**不因此跳过 KV**。算子级探针 skill **`msprobe-dump`** 放在 KV 之后（statistics · eager · 禁图） |
| Spec 接受率/长度异常 | `spec_acceptance` | 需 MTP/Eagle 等 speculative |
| 怀疑 KV / PD 传写出问题 | `dump_kv` +（有标杆时）对比 | 适用于有限异常 / `token_repeat` 等；detector 给坐标，定界靠对比；**无标杆时仍可先做单侧数值问题检查** |
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

无标杆时仍可：开 detector 确认异常类、落 report、抓单侧 `dump_kv`，并对该异常 dump **先做有效槽「数值问题」检查**（全零 / 有限非零 / NaN·Inf·范数零；未用槽另记，口径同 skills v5.20.10+）——**不必等清洁标杆**。报告里的 token ids 留给以后 force-feed。  
无标杆时不能：做 buggy vs ref 的 KV 首分歧，或可靠回答「从哪一层开始坏」。单侧 `.pt` 不能单独证明是写坏还是算坏；但「有效槽已出现数值问题」本身是可交付的事实。

**结论：** 无标杆时，Guard 的交付停在 **「问题类 + 可归档现场 +（若有 dump）单侧数值结论」**；这是合格的 **初步定界**，不是根因定位。标杆就绪后再走 §4 Step 5–6。

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
症状 triage →（看似必现则先验复现）→ 启 Guard（开 report+dump）→ 冒烟 → 压测抓命中
  → 脚本检查异常 dump 是否可读、齐全
  → 单侧先检有效槽「数值问题」（无标杆也可）
  → [有标杆] force-feed 抓清洁对照 → buggy vs ref 对账 → §5 十问
  → [无标杆] 停在「类 + 现场 + 单侧数值结论」，待补标杆
```

### Step 0 — Triage

按 §2 判断是否适合；不适合则明确停。若业务侧声称「必现 / 一请求就坏」，先做下面 **Step 0.5**，再按 §2.3 走无标杆停点或继续开 Guard。

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

启服细节见 [01_enable_and_start/README.md](../01_enable_and_start/README.md)。排障期建议：

1. 启动参数开热更，路径用**绝对路径**（容器/多进程下工作目录常变）：
   - `runtime_config_hot_reload=true`
   - `runtime_config_path` / `runtime_report_dir` / `runtime_dump_dir` 指到持久目录  
2. live JSON（或启动时 `runtime_config` 覆盖）里**同时开报告与 dump**，并打开要用的检测器；**务必** `save_sensitive_info: true`（否则没有 token ids，后续无法按原序列抓清洁对照）。

**排障推荐配置示例**（字段名与本项目 Guard runtime JSON 一致；阈值可按现场再调，此处给可直接套用的骨架）：

```jsonc
{
  "dump": {
    // N = 命中后自动 dump 的次数上限；按磁盘粗估：
    // N ≈ 磁盘剩余×0.7 / 单次请求 KV 快照大小，再与「预计要抓几份」取小
    "auto_max_times": 3,
    "auto_cooldown_seconds": 300,
    "manual_dump": false
  },
  "report": {
    "max_per_req": 1,
    "save_sensitive_info": true
  },
  "detector": {
    "token_repeat": {
      "enabled": true,
      "on_trigger": ["report", "dump_kv"]
    },
    "logits_finite": {
      "enabled": true,
      "on_trigger": ["report", "dump_kv"]
    }
    // 有 MTP/Eagle 等 speculative 时再开：
    // "spec_acceptance": { "enabled": true, "on_trigger": ["report", "dump_kv"] }
  }
}
```

说明：

- `on_trigger` 含 `"report"` + `"dump_kv"`：检测命中时既写报告，又落本请求 KV。  
- 若只想先确认「能不能写出报告」，可临时把 `auto_max_times` 设为 `0`、且 `on_trigger` 只留 `"report"`；通路通了再改回上表开 dump。  
- 检测漏检但问题已必现时，可改用 `dump.manual_dump = N`（**目标总次数**，不是剩余次数）手动抓异常 KV；`auto_max_times>0` 与正在生效的 `manual_dump` **不要同时开**。  
- 阈值细节（window 等）见 [03_detectors](../03_detectors/README.md) / skill `config-recommender`；排障开局先保证 **开检测 + 开 dump + 留 token ids**。

### Step 2 — Dump 管线冒烟（再压测）

1. 先确认 report JSON 能写出（可先只 `"report"`、`auto_max_times: 0`）。  
2. 再按 Step 1 打开 `dump_kv` 与合理的 `auto_max_times`（N）。  
3. 确认 last-PP 各 `tp*` 的 `.pt` 齐全。

### Step 3 — 压测抓真命中

- 有多份 report / sample 时：**优先查看看起来就错误的**（乱码 / 异常样本）。  
- 确认报告里已有 `prompt_token_ids` / `output_token_ids`（依赖 Step 1 的 `save_sensitive_info: true`）。  
- 误报目录及时清理腾盘。

### Step 4 — 检查异常 dump，并先做单侧数值问题

离线脚本在本仓 [06_agent_skills/scripts/](../06_agent_skills/scripts/)（与 [06 Agent Skills](../06_agent_skills/README.md) 同入口）：

```bash
export RG_DOCS=/path/to/runtime-guard-docs
SCRIPTS="$RG_DOCS/06_agent_skills/scripts"
python "$SCRIPTS/summarize_reports.py" --report-dir {REPORT}
python "$SCRIPTS/verify_request_kv.py" --report ... --kv-dir {KV_RANK_DIR}
```

**`verify_request_kv` 是什么：** 用脚本核对「这份异常请求的 KV dump 是否找得到、读得开、和 report 对得上（路径 / 分片大致齐全）」。  
它输出的 **PASS / FAIL 只表示 dump 文件是否够用来继续抓清洁对照**，**不是**案例结案四档里的「KV 一致 / 不一致」。

| 脚本结果 | 含义 | 下一步 |
|----------|------|--------|
| **PASS** | 异常侧 dump 可读、完整到足以继续 | 可先做单侧数值问题；再去抓清洁标杆做对比 |
| **FAIL** | dump 不够用 | **先修抓取**，不是「结案失败」：检查 dump 目录路径是否指对、`auto_max_times`（配额 N）是否够、`on_trigger` 是否含 `"dump_kv"`、各 `tp*` 分片是否齐 |

**单侧数值问题（无标杆也要做）：** dump 通过后，对异常侧有效槽先扫一遍——全零 / 有限非零 / NaN·Inf·范数零；未用槽另记（多数为 0，偶见有限非零；亦可有 NaN/Inf）。有数值问题就先写进事实；**不必等清洁标杆**。脚本与口径见 [ref-kv-dump](../06_agent_skills/ref-kv-dump/SKILL.md) / [scripts/README](../06_agent_skills/scripts/README.md)。

### Step 5 — 有标杆：同 token 序列抓 ref，再做 KV 对账

- 同模型、同拓扑、**同 MODE**（勿用 eager↔graph 当对照）。  
- 用 report 的 `prompt_token_ids` + `output_token_ids` **force-feed**（token-id API），禁止字符串重 tokenize。  
- Guard KV 对比只用 native `dump_kv`（不要把 msprobe / 临时自造 dumper **当成** KV 对比源）。  
- **`logits_finite` 命中后仍做 KV 对账**（先数值问题，再在干净格上算余弦）。生成很短时层定位可能变弱，但**不因此跳过 KV**。需要查「哪个算子先坏」时，再在 KV 之后开 **`msprobe-dump`**（殿后）。  
- 清洁标杆侧不应再亮 `logits_finite`（炸过的 dump 不能当标杆）。

### Step 6 — 首分歧与十问检查单

见 §5。完成后删除服务运行产生的临时全量 `kv_cache`（dump 输出的 `.pt` 小样证据保留即可）。

> 对比异常侧与清洁标杆时，先找**第一个已出 KV 问题**的 token/层（数值不对，或余弦明显偏低）。下面的检查单现为 **十问**（Q1–Q10）；旧文若写 Q1–Q5，含义已并入此表。

### 无标杆时的停点

完成 Step 3–4（含单侧数值问题）→ 标杆记「无」→ 转开发或等对照环境。不要伪造 ref。

---

## 5. KV 定界十问检查单（有 buggy+ref 时按序）

**前置：** 异常侧 dump 已通过 `verify_request_kv`（脚本确认 dump 可读齐全，**不是**结案档「KV 一致」）；并且已有 buggy + 清洁对照 dump。按序答下表，只填 **检查 outcome**。

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
