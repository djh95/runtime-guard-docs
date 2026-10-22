# S10′ · FullAttn recycle-zero（KV 一致→排除 KV）

公开自洽案例包。对照：[S01](../S01/)（dense **未复现**，不是漏检）。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 一致→排除 KV** |
| 检测 | **检出** |
| 三层率 | **65 / 20 / 79** |
| Detector | `token_repeat` |
| Origin | `both` |
| Guard pin | G2 f2aefd068 |
| 模型 | Qwen3-8B（英文并发负载） |
| Run | 10_fullattn_recycle_zero-20261016T181551|

## 1 · 现象

输出塌成短语复读或一串 `xxxx`。`token_repeat` 命中很多（detect 79 / 80 请求）。

**样本说明：** `evidence/samples/` 已归档标杆 run `T181551` 的 prompt+completion 文本（`xxxx` 塌缩；含 `api_response`）——供**阅读 / precision 核对**。tokenize 标杆以 report 内实际 `prompt_token_ids` 为准（见 [report_sample.json](./evidence/reports/report_sample.json)，本包有非空 ids）；detect=79 同见该 report（`token_repeat`）。

## 2 · 根因

FullAttention 不进 `needs_kv_cache_zeroing` 管线，回收 block 时 partial-tail 仍带脏 K/V（[#39283](https://github.com/vllm-project/vllm/pull/39283)、[#43741](https://github.com/vllm-project/vllm/pull/43741)）。

对照 S01：S01 是进了 zeroer 再 skip（且需 hybrid/量化 KV 才有目标症状）；S10′ 是 FullAttn **从来不进** zeroing，dense 回收即可打出塌缩。详见 [S01](../S01/)「为何 S01 复现不出、S10′ 可以」。

## 3 · Guard 结果

**检出。** 期望 `token_repeat`。归档 **65 / 20 / 79**（precision 可用 `evidence/samples/` 核对；detect 有 report）。结案档：**KV 一致→排除 KV**。

## 4 · 复现技巧

Overlay：强制 `needs_kv_cache_zeroing=False`，在 `BlockPool.get_new_blocks` 打 trigger。负载：concurrent 64 变长英文 + 16 条内容相同的 temp=0；util=0.35；不开 APC。

标杆 run=`T181551`（英文负载）。勿用顺序中文负载当标杆（CJK 启发式会虚抬 precision）。

## 5 · 定界分析
### 事实

- 现象：复读 / `xxxx` 塌缩（`evidence/samples/`）。
- 三层：65 / 20 / 79；detector：`token_repeat`。
- 归档 report：`prompt_token_ids` 非空（len=32）；有 `output_token_ids`。
- 本包已归档 KV 对比（cos_thresh=0.99；n_prompt=32 n_cmp_tokens=36；layers=72）。
- 标杆 vs 异常：对比窗口**全程一致**（min-over-layers cos ≥ thresh）；output 首 token 余弦=0.999995。
- 首不一致：无。

### 推断

- 对账一致 → **排除 KV cache** 作为本请求坏输出的必要原因。
- 坏输出仍不能从文本推出构造根因；转向非 KV 类（见案例背景/构造）。
- 无首不一致 → 推不出污染时机窗口。

### 结论

- 结案档：**KV 一致→排除 KV**（本请求对比窗口）。
- 尚未定界到具体算子/构造根因；分析不出 / 证据不足。

## 6 · 证据文件
| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格（Origin / 锚点 / overlay / knobs / 期望 detector） |
| `evidence/三层计数.json` | 三层明细（trigger / precision / detect） |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/samples/` | 坏输出原文（prompt + completion；自 T181551） |
| `evidence/reports/` | Guard detector 报告 |
| `evidence/kv_compare.json` | 最新 KV 标杆对比摘要（余弦 / 首不一致 / 结论） |

## 7 · 上游 PR 关系
| PR / 链接 | 角色 |
|-----------|------|
| [vLLM#39283](https://github.com/vllm-project/vllm/pull/39283) | **根因修复**（FullAttn 进入 zeroing 门控） |
| [vLLM#43741](https://github.com/vllm-project/vllm/pull/43741) | **同族相关** |
| [issue #39146](https://github.com/vllm-project/vllm/issues/39146) | 背景 issue |
