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

1. 在 **grammar 之前** 的预采样路径上，对 logits 做设备侧「是否全有限」检查。  
2. **默认 `item_sync=false`：** 先发起异步检查，不阻塞采样；**采样结束后再取结果**。此间 grammar 等可能改写 logits（例如 bitmask 写成 `-inf`），所以报告里的坏值类型（`finite_kind`）有时是改写后的样子；是否「曾经非有限」仍以预计算的行标志为准。  
3. **`item_sync=true`：** 预采样阶段就阻塞取回结果并解析坏值类型，与 grammar 前一致，但每步多一次 NPU→CPU 同步，更贵。  
4. **命中之后：** 解析是哪一行、哪类坏值、属于哪个请求；先入队，采样结束后统一处理出报告。

## 主要参数

| 字段 | 默认 | 含义 |
|------|------|------|
| `enabled` | `false` | 总开关 |
| `item_sync` | `false` | `true` = 同步取结果（坏值类型更准，更贵） |
| `on_trigger` | 含 `report` | 可加 `dump_kv` |

## 阶段与接线

- **Stage：** `before_sample`（包在 compute_logits 里）  
- 入队后的统一处理在 after-sample  
- 定位坏行属于哪个请求，靠 `query_start_loc`（查询序列起点；短写 qsl）。batch 偏短或错位时先做边界检查；对不上就**宁可不报**，避免 IndexError 或瞎猜 `req_id`。

## 误报 / 漏报提示

| 情况 | 建议 |
|------|------|
| 需要「grammar 前」精确 kind | `item_sync: true` |
| 只要尽早发现非有限 | 默认 async 即可 |
| 有 gate 命中但无 report | 查是否 unattributable（日志 warning） |

## 定界时怎么用

- 命中本身已较强：**数值路径已坏** 的粗定界。  
- 若要层定界：仍需 dump + 标杆（见 [02 §5](../02_problem_localization/README.md#5-kv-定界十问检查单有-buggyref-时按序)）。  
- 无标杆：交付「logits 非有限类 + report/单侧 dump」。

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
