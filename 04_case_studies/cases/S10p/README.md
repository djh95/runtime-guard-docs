# S10′ · FullAttn recycle-zero（复现未抓到）

公开自洽案例包。对照：[S01](../S01/)（dense **未复现**，不是漏检）。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **复现未抓到** |
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

**检出。** 期望 `token_repeat`。归档 **65 / 20 / 79**（precision 可用 `evidence/samples/` 核对；detect 有 report）。结案档：**复现未抓到**。

## 4 · 复现技巧

Overlay：强制 `needs_kv_cache_zeroing=False`，在 `BlockPool.get_new_blocks` 打 trigger。负载：concurrent 64 变长英文 + 16 条内容相同的 temp=0；util=0.35；不开 APC。

标杆 run=`T181551`（英文负载）。勿用顺序中文负载当标杆（CJK 启发式会虚抬 precision）。

## 5 · 定界分析

### 事实

- 现象 / 检测见上文钉点与 samples（或 reports）。
- **有效 KV 对账：无。** 本包曾归档的 `kv_compare.json` 及其中「首不一致 / 层号 / 余弦」结论**全部撤回**（新旧跑次混用、空 prompt、弱窗、全 NaN 占位等问题，不可信）。

### 推断

- 在重做**同一次异常请求**的有效异常 dump ↔ 标杆对账之前，**不能**得出「排除 KV」或「KV 不一致定界」。
- 坏输出 / 构造预期 ≠ 已证根因。

### 结论

- 结案档：**复现未抓到**（有异常或检出证据，但无有效异常 KV 可对账）。
- **尚未做有效 KV 对账**；分析不出 / 证据不足。


## 6 · 证据文件
| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格（Origin / 锚点 / overlay / knobs / 期望 detector） |
| `evidence/三层计数.json` | 三层明细（trigger / precision / detect） |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/samples/` | 坏输出原文（prompt + completion；自 T181551） |
| `evidence/reports/` | Guard detector 报告 |

## 7 · 上游 PR 关系
| PR / 链接 | 角色 |
|-----------|------|
| [vLLM#39283](https://github.com/vllm-project/vllm/pull/39283) | **根因修复**（FullAttn 进入 zeroing 门控） |
| [vLLM#43741](https://github.com/vllm-project/vllm/pull/43741) | **同族相关** |
| [issue #39146](https://github.com/vllm-project/vllm/issues/39146) | 背景 issue |
