# S10′ · FullAttn recycle-zero（PASS）

公开自洽案例包。对照：[S01](../S01/)（dense **FAIL（复现未出现）**，不是漏检结案）。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
| 三层率 | **65 / 20 / 79** |
| Detector | `token_repeat` |
| Origin | `both` |
| Guard pin | G2 f2aefd068 |
| 模型 | Qwen3-8B（英文并发负载） |
| Run | 10_fullattn_recycle_zero-20261016T181551 @ 160 cards 4,5 |

## 1 · 现象

输出塌成短语复读或一串 `xxxx`。`token_repeat` 命中很多（detect 79 / 80 请求）。

**样本说明：** 本仓仍 **无** `samples/`（无 prompt+completion 原文）。`precision=20` 仅来自 `layers.json` 计数，**勿当作已归档坏输出原文**。detect=79 现有 [evidence/reports/report_sample.json](./evidence/reports/report_sample.json)（`token_repeat`，自 T181551）。

## 2 · 根因

FullAttention 不进 `needs_kv_cache_zeroing` 管线，回收 block 时 partial-tail 仍带脏 K/V（[#39283](https://github.com/vllm-project/vllm/pull/39283)、[#43741](https://github.com/vllm-project/vllm/pull/43741)）。

对照 S01：S01 是进了 zeroer 再 skip（且需 hybrid/量化 KV 才有目标症状）；S10′ 是 FullAttn **从来不进** zeroing，dense 回收即可打出塌缩。详见 [S01](../S01/)「为何 S01 复现不出、S10′ 可以」。

## 3 · Guard 结果

**PASS。** 期望 `token_repeat`。归档 **65 / 20 / 79**（precision 仍无原文 completion 样本；detect 有 report）。

## 4 · 复现技巧

Overlay：强制 `needs_kv_cache_zeroing=False`，在 `BlockPool.get_new_blocks` 打 trigger。负载：concurrent 64 变长英文 + 16 条内容相同的 temp=0；util=0.35；不开 APC。

标杆 run=`T181551`（英文负载）。勿用顺序中文负载当标杆（CJK 启发式会虚抬 precision）。

## 5 · 教学要点

同大类 KV 脏读：**S10′ 能检**（recycle → `token_repeat`）；**S01** 在稠密栈上是 **FAIL（复现未出现）**（需 hybrid/量化 KV，dense 未见坏输出）。定界时不要只讲一个 detector。

## 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/status.json` | 跑批元数据（含远端 run 路径） |
| `evidence/layers.json` | 三层 65/20/79 |
| `evidence/reports/report_sample.json` | token_repeat report 样本（自 T181551） |
| `evidence/SPEC_excerpt.md` | SPEC / 上游锚点摘录 |
| `evidence/WHY_PASS.md` | 为何 PASS |

## 上游 PR 关系

| PR / 链接 | 角色 |
|-----------|------|
| [vLLM#39283](https://github.com/vllm-project/vllm/pull/39283) | **根因修复**（FullAttn 进入 zeroing 门控） |
| [vLLM#43741](https://github.com/vllm-project/vllm/pull/43741) | **同族相关** |
| [issue #39146](https://github.com/vllm-project/vllm/issues/39146) | 背景 issue |
