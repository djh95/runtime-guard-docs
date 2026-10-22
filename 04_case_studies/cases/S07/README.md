# S07 · W8A8 scale collapse → logits 有限乱码（KV 不一致→定界 · 弱窗）

公开自洽案例包。同属「有限分值 / KV·量化」话题的对照：[S01](../S01/)（dense **未复现**，不是漏检）。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 不一致→定界（弱窗/力度有限）** |
| 检测 | **乱码漏检** |
| 三层率 | **2624 / 1（跨请求内容相同×48） / 0** |
| Detector | 期望 `logits_finite` → **miss**（0 report） |
| Origin | `both` |
| Guard pin | G2 f2aefd068 |
| 模型 | Qwen3-8B-W8A8 TP2 |
| Scenario | `07_quant_scale_collapse` |
| Run | 07_quant_scale_collapse-20261016T084241 |

## 1 · 现象

这里能直接看到**真实的乱码 / 混合脚本垃圾输出**（不是评分把正常中文误判成异常），而且是**跨请求内容相同的乱码**×48（见 [④ 名词表](../../README.md#名词怎么读先看这里)：多次独立请求输出同一段垃圾，不是每次随机不同）。归档样本见 [evidence/samples/](./evidence/samples/)。这和 S01 那篇通顺散文不同。

## 2 · 根因

W8A8 dequant scale 崩溃（在 `deq_scale` 上 zero + 1e20）。属于 quant / scale 族。上游：[vLLM#37442](https://github.com/vllm-project/vllm/pull/37442)。更完整复现字段见 [evidence/规格说明.md](./evidence/规格说明.md)。

## 3 · Guard 结果

**乱码漏检。** `logits_finite` 已武装，detect=0——logits（采样前的分值）始终是有限数，没有 NaN/Inf；文字仍是乱码，故漏检。score 侧 `garbage_mixed_script`×48 且跨请求内容相同。结案档为 **KV 不一致→定界（弱窗/力度有限）**（有异常 dump，但对账窗弱）。

| 层 | 归档 |
|----|------|
| trigger / precision / detect | **2624 / 1（跨请求内容相同×48） / 0** |

status 里 precision 记成 1，但 samples + score 证实跨请求内容相同的乱码×48——**以 samples + score 为准**。

## 4 · 复现技巧

按本包 pin / 模型 / overlay 意图对齐三层率。Trigger 极高（2624）。不要强制写 NaN 或 token fill 伪造症状。

## 定界分析

### 事实

- 现象：有限分值乱码 + 乱码漏检；归档 dump 侧可用配对为旧 `logits_finite`（`output_token_ids` 仅 1 枚）。
- 本包已归档 KV 对比（cos_thresh=0.99；n_prompt=16 n_cmp_tokens=16；matched_layers=72）。
- 原 report `prompt_token_ids` 为空；同 prompt re-curl 后与异常 `output_token_ids` 合并再抓标杆。
- 首不一致：idx=0 role=prompt span=prompt min_cos=NaN @ layer_36。
- 后续是否恢复≈1：False；output 首 token 余弦=n/a（对比窗口无 output 槽）；仅 PD 复现：False。

### 推断

- 弱 dump 对账不一致 → **重开 KV 线**，但排除/坐实力度受限于 o=1 + re-curl ids，不能直接写成 W8A8 dequant 根因。
- 坏输出仍不可直接写成具体根因。

### 结论

- 结案档：**KV 不一致→定界（弱窗/力度有限）**；identical+garbage 形态 + 乱码漏检；弱 dump 与标杆不一致。
- 尚未定界到 W8A8 dequant / 具体写传路径；分析不出 / 证据不足。

## 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格（Origin / 锚点 / overlay / knobs / 期望 detector） |
| `evidence/三层计数.json` | 三层明细（trigger / precision / detect） |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/samples/` | prompt + completion 样本 |
| `evidence/kv_compare.json` | 最新 KV 标杆对比摘要（余弦 / 首不一致 / 结论） |

## 上游 PR 关系

| PR / 链接 | 角色 |
|-----------|------|
| [vLLM#37442](https://github.com/vllm-project/vllm/pull/37442) | **根因修复**（quant / dequant scale 族） |
