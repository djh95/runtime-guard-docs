# S45 · Top-k on −logits → unique garbage（FAIL+GAP）

公开自洽案例包。能检对照：[S43](../S43/)。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **FAIL+GAP** |
| 三层率 | **16 / 4 / 0**（现行；trigger/precision 随并发浮动，detect 为判定口径） |
| Detector | `token_repeat` + `logits_finite`（均 miss）；**乱码检测漏检** |
| Origin | `both`（constructed wrong-topk-direction） |
| 模型 | Qwen3-8B；**temp=0.8**（勿用 0） |
| Run | 按复现技巧复现（双树 + temp=0.8） |

## 1 · 现象

**各不相同（unique）** 的混合脚本垃圾文字；采样前分值始终有限，没有 NaN/Inf。内容相同计分会低估——`precision=4` **不能单独**当成「几乎没有坏输出」。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 根因

top-k / top-p 作用在 `-logits` 上再取反——保留最低-k / 倒置 nucleus。**不是**放大器。

## 3 · Guard 结果

**FAIL+GAP。** detect=0。异常已出现，但乱码检测漏检。勿用 amplifier-retune 刷检。

## 4 · 复现技巧与双树写入（必读）

本案例 overlay 同时改：

1. Ascend `vllm_ascend/platform.py`（boot 日志）  
2. **vLLM** `vllm/v1/worker/gpu/sample/sampler.py`（真正 flip）

因此：

- **正确：** `gen_s45_overlay.py` 分别写 **Ascend B** + **canonical/vllm**；**temp=0.8**。  
- **错误：** 只 `git apply` 到 Ascend B → `sampler.py: No such file or directory`；或 temp=0。

按复现技巧（双树 + temp=0.8）→ **16 / 4 / 0**（仍为 detect=0，与归档 GAP 一致）。

## 5 · 教学要点

1. 各不相同的有限乱码 + detect=0 → FAIL+GAP；对照 S43（magnitude 故障能检）。
2. 乱码样板对照 **S07**（跨请求相同）；**S01** 是 dense 未见坏输出的对照，不是乱码样板。
3. 环境：必须 **双树写入 + temp=0.8**。

## 定界分析

（**L1** = 检测停点 / **L2** = 问题类停点；**不是** Transformer 层号。见 [④ 名词表 · L1/L2](../../README.md#名词怎么读先看这里)。）

1. **现象与证据**——detector：detect=0（`token_repeat`+`logits_finite` 均 miss）→ **乱码检测漏检**。各不相同有限乱码见 `evidence/samples/`。
2. **排除（已做 / 应做）**——已确认异常已出现（非复现未出现）。无命中 report，包内未附 KV 对账；有 report 后可走重放 ids + KV 排除，勿写「Q1–Q5 不适用」仅因缺 prompt 快照。
3. **定界结论**——停在弱 **L2（问题类停点）**：top-k 打在 −logits / unique-garbage。**L1（检测停点）**：未检出。结案：FAIL+GAP；双树 + temp=0.8 → 16/4/0。

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
| （constructed wrong-topk-direction） | 无单一上游修复 PR；对照能检侧见 S43 |
