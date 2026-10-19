---
cursor:
  subagentId: "bc-fea3f65c-820d-58a1-a9ad-17d3943fe455"
---

# Runtime Guard 部署注意表 — 白话详解（2026-10-19）

**源表：** [`runtime-guard-docs` → `01_enable_and_start.md` §4「不同部署要注意什么」](https://github.com/djh95/runtime-guard-docs/blob/main/01_enable_and_start.md)  
（本地镜像：`runtime-guard-docs/01_enable_and_start.md` 约 L109–122；开篇 static idle 见同文件 L5。）  
**互补：** 同仓 ops/设计细节亦可对照 test 仓 `docs/runtime_guard_ops.md` / `runtime_guard_design.md`（与公开手册一致）。

本文把表里每一行拆成：拓扑是什么 → Guard 为何这样 → 运维要做什么 / 常见错 → 术语。

---

## 先懂几句总原则

Guard 挂在 **Model Runner v2** 上。为了少做事、少通信：

1. **检测 + 写 report**：只在 **last-PP 的 TP0**（「班长」）做。  
2. **KV dump `.pt`**：在 **last-PP 的每一个 TP** 各写一份本地 head 分片。  
3. **非 last PP**：不算 report、不参与 dump bus——别去那些 rank 的盘上找。  
4. 默认 detector/dump/热更 **全关** → **static idle**，热路径尽量旁路，开销可忽略。

---

## 术语小词典

| 术语 | 白话 |
|------|------|
| **TP（Tensor Parallel）** | 把一层算子切到多张卡并行；`tp0`/`tp1`… 是切分后的 rank。 |
| **PP（Pipeline Parallel）** | 把网络按层切成多段流水线；**last PP** = 最后一段（通常才有 logits/sample）。 |
| **DP（Data Parallel）** | 多份完整副本吃不同请求；彼此相对独立。 |
| **last-PP TP0** | 「最后一段流水线里的 0 号张量并行卡」。只有这里跑 detector、写 report JSON。 |
| **`tp*` dumps** | dump 目录形如 `dp*_tp0_pp*_cp*/`、`…_tp1_…`；TP>1 时要凑齐各 TP 才能拼完整 KV。 |
| **static idle** | detector/dump/热更能力都关时的「静默旁路」：不走 Guard 热路径壳，接近无 Guard。 |
| **绝对路径** | `/data/...` 这种，不依赖进程 cwd；容器/K8s/systemd 下 cwd 常变。 |
| **sync/dump** | 每 wave 的配置同步 +（若命中）KV dump 排队/D2H；PP 下逻辑集中在 last stage。 |
| **`manual_dump` / `done`** | 手动拍 dump 的水位计数；减到 0 时 JSON 会写回「关」。多进程共享同一 JSON 时，**每个进程内存里各自扣**，文件上的 `done/false` 时机可能交错。 |
| **`AscendAsyncOutput.get_output()`** | Async scheduling 下，采样后结果在异步输出对象上取回；Guard 的 after-sample 检测挂在这里，而不是同步 sample 返回瞬间。 |
| **`additional_config`** | `vllm serve` / `LLM()` 的 Ascend 扩展配置；`runtime_config_*` 等都塞这里。 |
| **v2 runner** | Model Runner v2；Guard **只接 v2**，v1 未接线。 |

---

## 逐行详解（对应源表）

### 1. 单卡

**拓扑：** 一张 NPU，无 TP/PP/DP 切分（或等价于 TP=1、PP=1、DP=1）。

**Guard 为何：** 单卡时 last-PP TP0 就是这张卡自己；路径与配置最简单。默认全关时走 **static idle**（见开篇），几乎无额外开销。

**运维要做 / 常见错：**
- 配置/报告/dump 路径尽量用 **绝对路径**（尤其后面要上容器）。  
- 别以为「没开 Guard」却去找 report——默认关就是 idle。  
- 需要观测时再显式开 detector（或热更）。

---

### 2. TP>1

**拓扑：** 同一层权重/激活按张量维切到多卡，每步要做 TP 集合通信。

**Guard 为何：** 采样与「文本级」异常只在输出侧完整可见 → **只在 last-PP 的 TP0 检测并写 report**，避免每张卡重复报、也避免非输出 rank 上强行取 output。  
KV 却是按 TP 切开存的 → **dump 时 last-PP 每个 TP 都要写自己的 `tp*` 目录**，事后再 stitch。

**运维要做 / 常见错：**
- 只在 TP0 的 report 目录找 JSON。  
- dump 后检查是否 **凑齐** `tp0`、`tp1`…；只有 `tp0` 时对照 ops：其它 TP 是否同波 `end_of_wave_sync`。  
- **不要**只用某一个 `tp*` 的 `.pt` 当「完整 KV」。

---

### 3. PP>1

**拓扑：** 模型按层拆成多段；请求像流水线穿过各 PP stage。

**Guard 为何：** logits/sample 发生在 **最后一段**；更早 PP 根本没有最终 token 文本可检。sync（配置/dump 名单）与 dump bus 也设计在 **last PP**。

**运维要做 / 常见错：**
- **别在早期 PP 的磁盘/日志里找 report 或完整 dump。**  
- 缺少更早 `pp*` 层的 `.pt` 是 **预期行为**，不是丢文件。  
- 拼 KV 时用 last PP 上各 `tp*` 即可。

---

### 4. DP>1

**拓扑：** 多份「整模」副本并行服务不同请求（数据并行）。

**Guard 为何：** 各 DP 副本有自己的请求流与本地 KV → **报告/dump 彼此独立**。若多个进程 **共享同一份** `runtime_config.json` 做 `manual_dump`，文件里的计数与「写回 false」是共享的，但 **每个进程内存里各自扣减** → 最坏大约 `num_DP × N` 次拍打。

**运维要做 / 常见错：**
- 按 DP（或按进程）分开看 report/dump，不要假设全集群只有一份。  
- 共享 JSON 时：`manual_dump: N` ≠「全集群一共 N 次」；某副本先写 `false` 可能让其它副本热更后提前停。  
- 需要精确配额时：每 DP 独立配置文件，或接受「偏多」并做好磁盘预算。

---

### 5. 多机

**拓扑：** 进程跨节点（TP/PP/DP 任一跨机）。

**Guard 为何：** 每个 rank 仍按「绝对路径 / 本地可见路径」读写；跨机若路径不一致会有的 rank 写成功、有的找不到目录。

**运维要做 / 常见错：**
- **路径同构**（每机相同绝对路径）或挂 **NFS/共享盘**（注意延迟与锁）。  
- **dump 优先本地盘**（`.pt` 又多又大）；共享盘可只放 config/report 索引。  
- 容器多机更要统一挂卷约定。

---

### 6. MoE

**拓扑：** 混合专家模型；路由 + 专家计算，Python/调度侧往往更忙。

**Guard 为何：** Guard 在 host 侧挂检测/同步壳；MoE 本身 Python 占比已高，**再开** detector/dump/热更，CPU 开销更显眼。默认关（static idle）通常就够生产。

**运维要做 / 常见错：**
- 生产默认保持关；排障再开，并做前后对比。  
- 不要把「MoE 慢」全怪到 Guard——先确认是否已离开 static idle。

---

### 7. Spec / MTP

**拓扑：** 投机解码 / Multi-Token Prediction：draft 多提 token，再被目标模型接受/拒绝。

**Guard 为何：** 普通 `token_repeat` / `logits_finite` 看的是最终采样文本或 logits；**接受率**异常要靠专用 detector **`spec_acceptance`**。非 Spec 部署开它没有意义（甚至干扰理解）。

**运维要做 / 常见错：**
- 仅 Spec/MTP 场景启用 `spec_acceptance`。  
- 排障时同时看接受率曲线与文本类 detector，勿混为一谈。

---

### 8. Async scheduling

**拓扑：** 调度与执行流水重叠；输出可能异步返回（`AsyncModelRunnerOutput` / Ascend 异步输出）。

**Guard 为何：** after-sample 检测挂在 **`AscendAsyncOutput.get_output()`**（结果真正取回时），而不是「同步 sample 函数刚返回」那一刻。因此请求在业务侧可能已 **finish**，而 dump/D2H 仍在收尾。

**运维要做 / 常见错：**
- finish 后稍等再查 dump 目录；看 `dump_skipped` / 日志是否仍在 drain。  
- **禁止**在非 output 的 TP rank 上乱调 `get_output()`（会卡 TP collective）——这是实现约束，不是运维开关。  
- 对比同步路径时，不要用「finish 瞬间盘上必有 `.pt`」当断言。

---

### 9. 容器 / K8s

**拓扑：** 进程跑在 Pod/容器里，文件系统与 cwd 由挂卷决定。

**Guard 为何：** 默认相对路径挂在 cwd，容器一重启或多副本同挂卷根目录，会 **互相覆盖** 或写丢。

**运维要做 / 常见错：**
- **挂持久卷**；`runtime_config_path` / report / dump 用绝对路径。  
- **按 Pod（或按 DP/副本）分子目录**，例如 `/data/rg/pod-a/report`。  
- 热更时保证各 replica 能读到各自（或约定共享）的 JSON。

---

### 10. Offline `LLM()`

**拓扑：** 不用 `vllm serve`，用 Python `LLM(...)` 离线推理。

**Guard 为何：** 同一套 **`additional_config`** 注入；但若 runner 不是 **v2**，Guard **根本没接线**，配了也白配。

**运维要做 / 常见错：**
- `LLM(..., additional_config={...})` 与 serve 同样带 `runtime_config_*`。  
- **确认 v2 runner**；v1 → 无 report 时先查这个，而不是先查 detector 阈值。  
- 0.30.0 及更早需先打 backport patch（见手册 05）。

---

## 源表原文（对照）

| 场景 | 注意 |
|------|------|
| 单卡 | 绝对路径；默认关时为 static idle（见开篇） |
| TP>1 | 检测/报告只在 last-PP TP0；dump 要凑齐各 `tp*` |
| PP>1 | sync/dump 只在 last PP；别在早期 PP 找报告 |
| DP>1 | 各副本独立报告/dump；共享 JSON 时 `manual_dump` 的 `done` 每进程独立 |
| 多机 | 路径同构或 NFS；dump 优先本地盘 |
| MoE | 开功能后 Python 占比更明显；默认关即可 |
| Spec / MTP | 才需要 `spec_acceptance` |
| Async scheduling | after-sample 在 `AscendAsyncOutput.get_output()`；finish 可能早于 dump |
| 容器 / K8s | 挂卷；按 Pod 分子目录，避免互相 overwrite |
| Offline `LLM()` | 同样走 `additional_config`；确认 v2 runner |

---

## 一句话记忆

**报告看 last-PP TP0；KV dump 凑齐 last-PP 所有 tp\*；默认关=static idle；路径用绝对路径；Spec 才开 spec_acceptance；Async 要等 get_output/dump 收尾；LLM() 必须 v2。**
