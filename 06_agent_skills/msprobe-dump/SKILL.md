---
name: runtime-guard-msprobe-dump
description: >-
  After logits_finite (or other non-finite numerical) hits, dump operator I/O
  statistics with msprobe (task=statistics) under vllm-ascend eager mode to
  find the first bad op. No graph/aclgraph mode. Not a Guard KV dump_kv path.
---

# msprobe 算子统计 dump（vllm-ascend）

**类型：原子 · 算子 I/O 统计采集。**  
**何时用：** Guard `logits_finite` 已检出（采样前 NaN/Inf），或明确要查「哪个算子先坏」。  
**何时不用：** 有限垃圾 / `token_repeat` 疑 KV → 走 [`ref-kv-dump`](../ref-kv-dump/SKILL.md)；Hang / OOM / 纯吞吐 → 换工具。

契约：[SKILLS_METADATA.md](../SKILLS_METADATA.md) · 分流：[investigation](../investigation/SKILL.md) · 上游文档：本机 `msprobe/docs/zh/user_guide/dump/vllm_dump_instruct.md`、`pytorch_data_dump_instruct.md`、`config_json_introduct.md`；vllm-ascend `docs/.../msprobe_guide.md`。

---

## 硬约束（本仓 keep-set / 排障默认）

1. **只要统计值** — `task: "statistics"` + `summary_mode: "statistics"`（Max/Min/Mean/Norm 等）。**不要**默认开 `tensor` 全量落盘。  
2. **不支持图模式** — 必须 **eager**：`--enforce-eager`（使 `cudagraph_mode == NONE`）。图模式走 `AclGraphDumper` / `aclgraph_dump`，本 skill **不做**。  
3. **Guard KV 与 msprobe 分开** — 勿把 msprobe 产物当 `dump_kv` 对比源；`logits_finite` 命中后 **跳过** KV ③/④。  
4. **安装** — `pip install mindstudio-probe`（或源码装）。容器内 `import msprobe` 失败先装再跑。

源码锚点（vllm-ascend）：`NPUModelRunner` 在 `dump_config_path` 非空且 **eager** 时 `PrecisionDebugger(dump_cfg)`；`execute_model` 路径 `start → … → stop → step`（见 `worker/model_runner_v1.py`）。

---

## 推荐 config（statistics · L1）

```json
{
  "task": "statistics",
  "dump_path": "/workspace/runtime-guard/verify-docs/msprobe_dump/Sxx",
  "rank": [],
  "step": [],
  "level": "L1",
  "async_dump": false,
  "extra_info": false,
  "statistics": {
    "scope": [],
    "list": [],
    "tensor_list": [],
    "data_mode": ["all"],
    "summary_mode": "statistics"
  }
}
```

| 字段 | 本 skill 默认 |
|------|----------------|
| `task` | **`statistics`**（仅统计） |
| `level` | **`L1`**（API/算子级；轻量）。需要 module 结构再升 `mix`/`L0`（L0/`mix` 的 `start` 需 model，ascend runner 已传） |
| `summary_mode` | **`statistics`**（勿默认 md5/xor） |
| `step` | `[]` = 各 iteration；可收窄到出问题的 token step |
| `list` / `scope` | 初扫留空；锁定嫌疑算子后再填子串或全名 |
| `request_id` | 可选；指定请求时配合 `VLLM_DISABLE_REQUEST_ID_RANDOMIZATION=1` + `X-Request-ID`（config 里常写 `chatcmpl-<id>`） |

可选对照：`task: "nan_check"` 查寄存器 NaN/Inf（仍非 KV）。

---

## 启用方式（vllm-ascend）

**优先** `--additional-config`（已集成，无需改 runner）：

```bash
export TORCHDYNAMO_DISABLE=1   # 遇 dynamo 报错可开
# 可选：钉 request
# export VLLM_DISABLE_REQUEST_ID_RANDOMIZATION=1

python -m vllm.entrypoints.openai.api_server \
  --model … --dtype float16 \
  --enforce-eager \
  --tensor-parallel-size 2 \
  --additional-config '{"dump_config_path":"/path/to/msprobe_config.json"}'
```

也可用内联 `dump_config`（工厂会落成临时 path）。**必须**带 `--enforce-eager`。

发一条短请求（temp=0）触发 `start→forward→stop→step`。多卡看 `dump_path/step*/rank*/`。

---

## 读结果（找首坏算子）

落盘以 **`dump.json`** 为主（statistics 不落完整 `.pt`）。每条 API/Module 的 input/output 含 `dtype` / `shape` / **`Max`/`Min`/`Mean`/`Norm`（或 L2norm）**。

**扫法（粗→细）：**

1. 按调用序扫 `dump.json`，找 **首个** Max/Min/Mean/Norm 出现 **NaN/Inf** 或明显爆炸的条目。  
2. 记录算子全名（如 `Torch.xxx` / `Functional.xxx` / `npu_*`）与 forward/backward、入出参序号。  
3. 需要时收窄 `statistics.list` / `scope` 或升 `level=mix` 再跑一轮（仍 statistics）。  
4. 有清洁对照时：同 config 抓 ref dump，用 `msprobe compare` / `graph_visualize`（可选；本 skill 最小交付是 **问题侧首坏算子名 + dump_path**）。

**不要：** 用 statistics 结果冒充 Guard `kv_compare`；在图模式/未 eager 下硬跑本流程。

---

## 与 Guard 编排的衔接

```text
logits_finite 命中
  → investigation：跳过 ref-kv-dump / ③④
  → 本 skill：eager + statistics dump
  → 交付：首坏算子（或「未在 dump.json 见非有限统计」+ 路径）
```

`token_repeat` / 有限异常疑 KV → **不要**先开本 skill。

---

## forbidden

- 图模式 / aclgraph / 未 `--enforce-eager` 当本 skill 默认路径  
- 默认 `task=tensor` 全量落盘（磁盘爆炸）  
- 把 msprobe dump 当作 native `dump_kv` 对比源  
- `logits_finite` 后仍空耗 KV 对账，或把 NaN KV 写成「复现未抓到」/ 伪层定位  

## Related

`investigation` · `ref-kv-dump` · `analysis` · `config-recommender`
