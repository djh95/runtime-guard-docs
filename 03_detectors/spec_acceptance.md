# 检测算法：`spec_acceptance`

投机解码（MTP / Eagle 等）接受率与接受长度漂移检测。

## 源码 / 配置

| 项 | URL |
|----|-----|
| 实现 | https://github.com/vllm-project/vllm-ascend/blob/main/vllm_ascend/observability/runtime_guard/detector/spec_acceptance.py |
| 功能说明 | https://github.com/vllm-project/vllm-ascend/blob/main/docs/source/user_guide/feature_guide/runtime_guard.md |

相关 PR：

| 说明 | URL |
|------|-----|
| 检测器基础框架合入 PR | https://github.com/vllm-project/vllm-ascend/pull/16849 |
| None accepted / 空 step 截断鲁棒修复 PR | https://github.com/vllm-project/vllm-ascend/pull/18644 |

## 解决什么问题

- Spec 路径上 **接受率过低/过高** 且伴随长度比异常，提示 draft/verify 或统计链路异常。  
- 仅在开启 speculative decoding、且 runner 能提供 accept 统计时有意义。

**不能：** 在无 speculative 时使用；不能单独证明是 draft 模型还是 verify 模型的权重问题。

## 算法要点

1. Stage：`after_spec`（经 sample 路径 `check_after_spec`；v2 在 `postprocess_sampled` stash 接受统计）。  
2. 每 req 维护滑动窗口：`(accepted_draft, draft_len, sampled_ids, accepted_ids)`。  
3. 窗口内估计接受率与长度比；低于 `low_threshold` 且长度比异常，或高于 `high_threshold` 且长度比异常 → 告警。  
4. `accepted_token_nums` 等为 `None` / 短 batch 时安全跳过或截断，避免崩溃。  
5. 告警事件日志在 TP0 做输出节流，避免日志刷屏。

## 主要参数（默认）

| 字段 | 默认 | 含义 |
|------|------|------|
| `enabled` | `false` | 总开关 |
| `window` | `10` | 滚动窗口 |
| `low_threshold` | `0.3` | 低接受率阈 |
| `len_low_threshold` | `1.4` | 低率时的长度比阈 |
| `high_threshold` | `0.96` | 高接受率阈 |
| `len_high_threshold` | `2.8` | 高率时的长度比阈 |
| `on_trigger` | 含 `report` | 可加 `dump_kv` |

## 阶段与接线

- **Stage：** `after_spec`  
- 无 `speculative_config` / 无 stash 统计 → 检测跳过（不崩）。  
- 报告滚动窗口内可能存在空 step `[]`，内部已做安全截断处理，不会引发异常。

## 误报 / 漏报提示

| 情况 | 建议 |
|------|------|
| 未开 MTP 却 enabled | 关闭；无意义且浪费 |
| 冷启前几步接受率不稳 | 加大 `window` 或先预热再看 |
| 只关心崩溃防护 | 可只开 report，慎开高频 dump |

## 定界时怎么用

- 命中 → 「spec 接受行为异常」粗定界。  
- 深层仍依赖 dump + 标杆或独立的 draft/verify 对照实验（超出 Guard 自动范围）。

## 最小配置

```json
// 仅用于临时问题排查，不建议业务环境长期启用
{
  "detector": {
    "spec_acceptance": {
      "enabled": true,
      "window": 10,
      "low_threshold": 0.3,
      "on_trigger": ["report"]
    }
  }
}
```
