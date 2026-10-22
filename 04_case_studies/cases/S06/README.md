# S06 · MoE routing bias / topk→0（KV 不一致→定界 · 唯一公开 MoE）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 不一致→定界** |
| 检测 | **检出** |
| 三层率 | **70 / 2 / 1** |
| Detector | `token_repeat` |
| Origin | `both` |
| Guard pin | G2 f2aefd068 |
| 模型 | DeepSeek-V2-Lite |
| Run | 06_moe_routing_bias-20261020T190354 |
| 备注 | detect=1 来自钉点 `token_repeat` report×1（`prompt_token_ids` 非空 len=17；与 KV 对账同一跑次）；与 `三层计数.json` 一致 |

## 1 · 现象

归档样本为复读塌缩（如「学德任任任…」）；有 `token_repeat` 报告（含非空 `prompt_token_ids`）。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 案例背景/构造

Overlay / 上游 PR 意图：错误 router bias / mask 类（非 bit-exact CUDA）→ 错专家。对外保留案例 **只留这一例** MoE。上游：[#38989](https://github.com/vllm-project/vllm/pull/38989)、[#60946](https://github.com/vllm-project/vllm/pull/60946)。**本案例构造预期根因不在 KV。** 构造已知 ≠ 定界从坏输出推出。

## 3 · Guard 结果

**检出。** detect 以归档 `reports/report_*.json`（`token_repeat`×1）为准。


## 4 · 复现技巧

按 pin / 模型 / overlay 对齐三层率。标杆是本包钉点（70 / 2 / 1 · run `20261020T190354`）。

## 5 · 定界分析
### 事实

- 本包已归档 KV 对比（cos_thresh=0.99；n_prompt=17 n_cmp_tokens=25；matched_layers=54）。
- 首不一致：idx=0 role=prompt span=prompt min_cos=-0.308082 @ layer_48。
- 后续是否恢复≈1：False；output 首 token 余弦=0.041545；仅 PD 复现：False。

### 推断

- 对账不一致 → **重开 KV 线**（写坏 / 传坏 / 脏读等仍可能）。
- 坏输出仍不可直接写成具体根因。
- 首不一致在 prompt 段 → 偏向 prefill 侧污染时机（需结合是否恢复、仅 PD）。

### 结论

- 结案档：**KV 不一致→定界**（重开 KV 线）。
- 尚未定界到具体写/传路径；分析不出 / 证据不足。

## 6 · 证据文件
| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格（Origin / 锚点 / overlay / knobs / 期望 detector） |
| `evidence/三层计数.json` | 三层明细（trigger / precision / detect） |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/samples/` | prompt + completion 样本（**阅读 / 现象核对**；非 tokenize 标杆） |
| `evidence/reports/` | Guard detector 报告 |
| `evidence/kv_compare.json` | 最新 KV 标杆对比摘要（余弦 / 首不一致 / 结论） |

## 7 · 上游 PR 关系
| PR / 链接 | 角色 |
|-----------|------|
| [vLLM#38989](https://github.com/vllm-project/vllm/pull/38989) | **根因类比**（MoE routing bias dtype） |
| [vLLM#60946](https://github.com/vllm-project/vllm/pull/60946) | **同族相关**（PCP MoE padding mask） |
