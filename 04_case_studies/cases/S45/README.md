# S45 · Top-k on −logits → unique garbage（复现未抓到）

公开自洽案例包。能检对照：[S43](../S43/)。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **复现未抓到** |
| 检测 | **乱码漏检** |
| 三层率 | **16 / 4 / 0**（现行；trigger/precision 随并发浮动，detect 为判定口径） |
| Detector | `token_repeat` + `logits_finite`（均 miss）；**乱码检测漏检** |
| Origin | `both`（constructed wrong-topk-direction） |
| Guard pin | G2 · `f2aefd068c4bd299d91cf0a1fdf642a3f327308f` |
| 模型 | Qwen3-8B；**temp=0.8**（勿用 0） |
| Run | 按复现技巧复现（双树 + temp=0.8） |

## 1 · 现象

**各不相同（unique）** 的混合脚本垃圾文字；logits 始终有限，没有 NaN/Inf。内容相同计分会低估——`precision=4` **不能单独**当成「几乎没有坏输出」。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 根因

top-k / top-p 作用在 `-logits` 上再取反——保留最低-k / 倒置 nucleus（构造故障本身；不是靠伪造 NaN/填复读 token 硬造症状）。

## 3 · Guard 结果

**乱码漏检。** detect=0。异常已出现，detector 未命中；manual dump 已完成有效对账。结案档：**复现未抓到**。

## 4 · 复现技巧（双树写入 · 必读）

本案例 overlay 同时改：

1. Ascend `vllm_ascend/platform.py`（boot 日志） 
2. **vLLM** `vllm/v1/worker/gpu/sample/sampler.py`（真正 flip）

因此：

- **正确：** `gen_s45_overlay.py` 分别写 **Ascend B** + **canonical/vllm**；**temp=0.8**。 
- **错误：** 只 `git apply` 到 Ascend B → `sampler.py: No such file or directory`；或 temp=0。

按复现技巧（双树 + temp=0.8）→ **16 / 4 / 0**（仍为 detect=0，乱码漏检）。

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
| `evidence/samples/` | prompt + completion 样本 |

## 7 · 上游 PR 关系
| PR / 链接 | 角色 |
|-----------|------|
| （constructed wrong-topk-direction） | 无单一上游修复 PR；对照能检侧见 S43 |
