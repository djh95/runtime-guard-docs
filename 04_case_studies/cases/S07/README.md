# S07 · W8A8 scale collapse → 无 NaN 乱码（复现未抓到）

公开自洽案例包。对照：[S01](../S01/)（dense **未复现**，不是漏检）。本包是**真有乱码**，但 logits 没有 NaN/Inf，专用 NaN 检测抓不住。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **复现未抓到** |
| 检测 | **乱码漏检** |
| 三层率 | **2624 / 1（跨请求内容相同×48） / 0** |
| Detector | 期望 `logits_finite` → **miss**（**0 report**；包内无 detector 报告） |
| Origin | `both` |
| Guard pin | G2 f2aefd068 |
| 模型 | Qwen3-8B-W8A8 TP2 |
| Scenario | `07_quant_scale_collapse` |
| Run | 07_quant_scale_collapse-20261016T084241 |

## 1 · 现象

这里能直接看到**真实的乱码 / 混合脚本垃圾输出**（不是评分把正常中文误判成异常），而且是**跨请求内容相同的乱码**×48（见 [④ 名词表](../../README.md#名词怎么读先看这里)）。归档样本见 [evidence/samples/](./evidence/samples/)。这和 S01 那篇通顺散文不同。

## 2 · 根因

W8A8 dequant scale 崩溃（在 `deq_scale` 上 zero + 1e20）。属于 quant / scale 族。上游：[vLLM#37442](https://github.com/vllm-project/vllm/pull/37442)。更完整复现字段见 [evidence/规格说明.md](./evidence/规格说明.md)。构造纪律（origin-faithful：禁止强制写 NaN / token fill）见规格与 overlay，**不是**复现负载技巧。

## 3 · Guard 结果

**乱码漏检。** 开了 `logits_finite`（抓 logits 里的 NaN/Inf），本包乱码的 logits 始终有限 → **detect=0**，**没有** detector report，也**不应**指望「检出后自动 dump」。文字坏了靠 **samples** 看见，不靠 report。

| 层 | 归档 |
|----|------|
| trigger / precision / detect | **2624 / 1（跨请求内容相同×48） / 0** |

status 里 precision 记成 1，但 samples + score 证实跨请求内容相同的乱码×48——**以 samples + score 为准**。

## 4 · 复现技巧

按本包 pin / 模型 / overlay 对齐三层率即可。Trigger 极高（2624）。

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
| `evidence/samples/` | prompt + completion 样本（**认乱码靠这里**） |

## 7 · 上游 PR 关系

| PR / 链接 | 角色 |
|-----------|------|
| [vLLM#37442](https://github.com/vllm-project/vllm/pull/37442) | **根因修复**（quant / dequant scale 族） |
