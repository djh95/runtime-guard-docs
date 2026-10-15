# 检测算法：`logits_finite`

采样前 logits 行是否全为有限值（NaN/Inf 检测）。

## 源码 / 配置

| 项 | URL |
|----|-----|
| 实现 | https://github.com/vllm-project/vllm-ascend/blob/main/vllm_ascend/observability/runtime_guard/detector/logits_finite.py |
| 功能说明 | https://github.com/vllm-project/vllm-ascend/blob/main/docs/source/user_guide/feature_guide/runtime_guard.md |

相关 PR：

| 说明 | URL |
|------|-----|
| 检测器基础框架合入 PR | https://github.com/vllm-project/vllm-ascend/pull/16849 |
| QSL边界鲁棒修复 PR | https://github.com/vllm-project/vllm-ascend/pull/18644 |

## 解决什么问题

- 采样前出现 **非有限 logits**（数值爆炸、污染）。  
- 给「乱码 / 异常输出是否已在 logits 阶段坏掉」的强信号。

**不能：** 指出是哪一层算坏；不能替代 KV 对比。无法归属到具体 `req_id` 的数据行仅输出 warning 日志，不会生成猜测信息或无有效请求信息的空报告。

## 算法要点

1. 在 **grammar 之前** 的 pre-sample 路径对 logits 做 device `isfinite` → all-finite gate。  
2. **默认 `item_sync=false`：** 非阻塞 D2H gate，在 after-sample 的 deferred 路径再 `.item()`；期间 grammar 等可能改写 logits（如 bitmask → `-inf`）。gate 用的 `row_finite` 仍基于预计算；命中时的 `finite_kind` 可能看到改写后数值。  
3. **`item_sync=true`：** pre-sample 阻塞 `.item()` 并解析 kind，与 grammar 前一致，但每步引入额外 NPU‑CPU（D2H）设备同步开销。  
4. 命中 → 解析坏行 / kind / req；enqueue；after-sample drain。

## 主要参数

| 字段 | 默认 | 含义 |
|------|------|------|
| `enabled` | `false` | 总开关 |
| `item_sync` | `false` | `true` = 同步 gate（更准 kind，更贵） |
| `on_trigger` | 含 `report` | 可加 `dump_kv` |

## 阶段与接线

- **Stage：** `before_sample`（compute_logits wrap 内）  
- Deferred / drain：after-sample  
- 归因依赖 `query_start_loc`；短/错位 qsl 时做边界保护，避免 IndexError，无法归属则不瞎报。

## 误报 / 漏报提示

| 情况 | 建议 |
|------|------|
| 需要「grammar 前」精确 kind | `item_sync: true` |
| 只要尽早发现非有限 | 默认 async 即可 |
| 有 gate 命中但无 report | 查是否 unattributable（日志 warning） |

## 定界时怎么用

- 命中本身已较强：**数值路径已坏** 的粗定界。  
- 若要层定界：仍需 dump + 标杆（见 [02](../02_problem_localization.md)）。  
- 无标杆：交付「logits 非有限类 + report/单侧 dump」即可，勿宣称层结论。

## 最小配置

```json
// 仅用于临时问题排查，不建议业务环境长期启用
{
  "detector": {
    "logits_finite": {
      "enabled": true,
      "item_sync": false,
      "on_trigger": ["report", "dump_kv"]
    }
  },
  "dump": { "auto_max_times": 2 }
}
```
