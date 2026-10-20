# S07 · W8A8 scale collapse → logits 有限乱码（FAIL+GAP）

公开自洽案例包。同属「有限分值 / KV·量化」话题的对照：[S01](../S01/)（dense **复现未出现**，不是漏检结案）。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **FAIL+GAP** |
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

**判定：FAIL+GAP。** `logits_finite` 已武装，detect=0——logits（采样前的分值）始终是有限数，没有 NaN/Inf；文字仍是乱码，故漏检。score 侧 `garbage_mixed_script`×48 且跨请求内容相同。

| 层 | 归档 |
|----|------|
| trigger / precision / detect | **2624 / 1（跨请求内容相同×48） / 0** |

status 里 precision 记成 1，但 samples + score 证实跨请求内容相同的乱码×48——**以 samples + score 为准**。

## 4 · 复现技巧

按本包 pin / 模型 / overlay 意图对齐三层率。Trigger 极高（2624）。不要强制写 NaN 或 token fill 伪造症状。

## 5 · 教学要点

1. **S07** = 有乱码 + detector miss → **FAIL+GAP**；**S01 dense** = 无坏输出 → **FAIL（复现未出现）**——勿并成同一漏检族（根因也不同：quant scale vs KV skip-zero）。
2. 需要 garbled-text / 跨请求内容相同类 detector；仅靠 `logits_finite` 抓不住有限乱码。

## 定界分析

1. **L1 detect 停点**——detect=0：`logits_finite` miss（logits 仍有限，无 NaN/Inf）→ **乱码检测漏检**。
2. **L2 class-hint**——弱 L2——跨请求内容相同的乱码（samples identical+garbage）。
3. **标杆 / Q1–Q5（KV 排除）**——空 prompt / 包内暂无 buggy+ref **不等于**「Q1–Q5 不适用」。有 report 即可：同 prompt 再 curl 抓服务端 `prompt_token_ids`，与异常 `output_token_ids` 合并后抓标杆 KV，对比异常 KV（一致→排除 KV；不一致→重开 KV 线）。**本案归档尚未附 KV 对比结论**；现行对外结案停在 L1+L2+现象。
4. **结合现象**——见 `evidence/samples/`。
5. **结案要点**——FAIL+GAP：异常已出现且 detect=0。

## 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格（Origin / 锚点 / overlay / knobs / 期望 detector） |
| `evidence/三层计数.json` | 三层明细（trigger / precision / detect） |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/samples/` | prompt + completion 样本 |


## 上游 PR 关系

| PR / 链接 | 角色 |
|-----------|------|
| [vLLM#37442](https://github.com/vllm-project/vllm/pull/37442) | **根因修复**（quant / dequant scale 族） |
