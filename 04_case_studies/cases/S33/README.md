# S33 · Incomplete softcap（复现未抓到）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **复现未抓到** |
| 检测 | **检出** |
| 三层率 | **130 / 17 / 48**（现行；detect=48/48；trigger/precision 随并发浮动，detect 为判定口径） |
| Detector | `token_repeat` |
| Origin | `both`（constructed softcap class） |
| Guard pin | G2 · `f2aefd068c4bd299d91cf0a1fdf642a3f327308f` |
| 模型 | Qwen3-8B |
| Run | 双树 + 河名句 |

## 1 · 现象

`1.1.1…` 模式；`token_repeat`×48。

## 2 · 根因

做了 `÷cap + tanh`，却 **跳过 `*cap` rescale**；boot 强制 cap=30。不等于 S20 的 overflow / `!!!!`。上游族：[vLLM#56579](https://github.com/vllm-project/vllm/pull/56579)。

## 3 · Guard 结果

**检出。** 现行 **130 / 17 / 48**。结案档：**复现未抓到**。

## 4 · 复现技巧（双树写入 · 必读）

softcap 改在 **vLLM** 的 `logits_processor.py`，同时 Ascend `platform.py` 也要打 boot/trigger。因此：

- **正确：** 跑 `gen_s33_overlay.py`——分别写入 **Ascend B** 与 **canonical vllm**。  
- **负载（与 S25/S26 同族现行复现）：** prompt = `Name one famous river. One short English sentence. id={i}.`，**48 路同时发请求**。

只对 Ascend B 做 `git apply`（缺 vLLM 树）会 PATCH_FAIL。  
**历史错跑：** 「中文回声式」prompt + 少量串行请求 → 打不出 `1.1.1…` 数字复读（复现条件不对）。

可用 `scripts/apply_anomaly_overlay.sh` 识别双树 patch，但 **仍推荐 gen_***。

本包以归档的 **incomplete softcap** 为准（不是 S20 overflow）。

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
| `evidence/reports/` | Guard detector 报告 |

## 7 · 上游 PR 关系
| PR / 链接 | 角色 |
|-----------|------|
| [vLLM#56579](https://github.com/vllm-project/vllm/pull/56579) | **同族相关**（softcap）；本包为 incomplete rescale 构造 |
