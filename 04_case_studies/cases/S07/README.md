# S07 · W8A8 scale collapse → logits 有限乱码（GAP）

公开自洽案例包。同缺口族对照：[S01](../S01/)。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **FAIL+GAP** |
| 三层率 | **2624 / 1（跨请求内容相同×48） / 0** |
| Detector | `logits_finite`（miss） |
| Origin | `both` |
| Guard pin | G2 f2aefd068 |
| 模型 | Qwen3-8B-W8A8 TP2 |
| Scenario | `07_quant_scale_collapse` |
| Run | 07_quant_scale_collapse-20261016T084241 |

## 1 · 现象

这里能直接看到**真实的乱码 / 混合脚本垃圾输出**（不是评分把正常中文误判成异常），而且是**跨请求内容相同的乱码**×48（见 [④ 名词表](../../README.md#名词怎么读先看这里)：多次独立请求输出同一段垃圾，不是每次随机不同）。归档样本见 [evidence/samples/](./evidence/samples/)。这和 S01 那篇通顺散文不同。

## 2 · 根因

W8A8 dequant scale 崩溃（在 `deq_scale` 上 zero + 1e20）。属于 quant / scale 族。上游：[vLLM#37442](https://github.com/vllm-project/vllm/pull/37442)。更完整字段见 [evidence/SPEC_excerpt.md](./evidence/SPEC_excerpt.md)。

## 3 · Guard 结果

**判定：FAIL+GAP。** `logits_finite` 已武装，detect=0——logits（采样前的分值）始终是有限数，没有 NaN/Inf；文字仍是乱码，故漏检。score 侧 `garbage_mixed_script`×48 且跨请求内容相同。

| 层 | 归档 |
|----|------|
| trigger / precision / detect | **2624 / 1（跨请求内容相同×48） / 0** |

status 里 precision 记成 1，但 samples + score 证实跨请求内容相同的乱码×48——**以 samples + score 为准**。

## 4 · 复现

按本包 pin / 模型 / overlay 意图对齐三层率。Trigger 极高（2624）。不要强制写 NaN 或 token fill 伪造症状。历史大批量跑数不在本仓；对外以本包为准。

## 5 · 别人按包能核对什么

与 S01 同属「logits 数值有限、文字仍是乱码」漏检族，根因不同（quant scale vs KV skip-zero）。需要 garbled-text / 跨请求内容相同类 detector。公开案例材料写全再对外。
