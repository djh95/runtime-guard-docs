# 检测算法：`token_repeat`

滑动窗口局部「复读」检测（不依赖 logprobs）。

## 源码 / 配置

| 项 | URL |
|----|-----|
| 实现 | https://github.com/vllm-project/vllm-ascend/blob/main/vllm_ascend/observability/runtime_guard/detector/token_repeat.py |
| 功能说明中的 detectors 表 | https://github.com/vllm-project/vllm-ascend/blob/main/docs/source/user_guide/feature_guide/runtime_guard.md |

相关 PR：

| 说明 | URL |
|------|-----|
| 检测器基础框架合入 PR | https://github.com/vllm-project/vllm-ascend/pull/16849 |

## 解决什么问题

- 输出在局部窗口内反复出现相同 token（卡词、复读）。  
- 作为偶发质量问题的 **轻量第一探测器**。

**不能：** 区分「模型策略性重复」与「实现 bug」；不能单独完成 KV 层定界。

## 算法要点

1. 消费 after-sample 累计输出流（每 token 只 fold 一次）。  
2. 对非 `ignore_token_ids` 的 token：`score =` 当前内容窗口内该 id 已出现次数；写入窗口并更新频次。  
3. `repeat_sum` = 最近 `window` 个 score 之和。  
4. 当 `content_tokens_seen >= min_tokens` 且 `repeat_sum > repeat_sum_threshold`，连续满足 `consecutive_hits` 次 → 告警。

## 主要参数（默认）

| 字段 | 默认 | 含义 |
|------|------|------|
| `enabled` | `false` | 总开关 |
| `window` | `32` | 内容滑动窗口 |
| `repeat_sum_threshold` | `64` | `repeat_sum` 超阈才计一次 hit |
| `min_tokens` | `32` | 内容 token 预热；`0` 表示不预热 |
| `consecutive_hits` | `1` | 连续超阈步数 |
| `ignore_token_ids` | `[]` | 不计入窗口的 id（如特殊 pad） |
| `on_trigger` | 含 `report` | 可加 `dump_kv` |

热更新修改 `window` 参数时，实现会清空 per‑req 状态与已告警集合，避免旧窗口配置的历史状态锁死判定结果。

## 阶段与接线

- **Stage：** `after_sample`  
- 依赖 host 侧已 trim 的 sampled ids（async / AsyncOutput 路径在 D2H 之后）。  
- CPU 侧经 ActionQueue 执行，不阻塞 finish 等待。

## 误报 / 漏报提示

| 情况 | 建议 |
|------|------|
| 合法长重复（歌词、列表） | 提高 `repeat_sum_threshold` / `consecutive_hits`，或加 ignore |
| 短句偶发重复漏报 | 降低 threshold，或减小 `min_tokens` |
| 只开 report 无现场 | `on_trigger` 加 `dump_kv` 并设 `auto_max_times` |

## 定界时怎么用

1. 命中 → 归档 report（建议 `save_sensitive_info: true`）。  
2. 需要层定界 → 加 dump + 有标杆时走 [02](../02_problem_localization/README.md) Q1–Q5。  
3. 无标杆 → 停在「复读类 + 现场」，见 [02 §2.3](../02_problem_localization/README.md)。

## 最小配置

```json
// 仅用于临时问题排查，不建议业务环境长期启用
{
  "detector": {
    "token_repeat": {
      "enabled": true,
      "on_trigger": ["report", "dump_kv"],
      "window": 32,
      "repeat_sum_threshold": 64
    }
  },
  "dump": { "auto_max_times": 3 }
}
```
