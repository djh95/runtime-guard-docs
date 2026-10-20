# S45 · Top-k on −logits → unique garbage（FAIL+GAP）

公开自洽案例包。能检对照：[S43](../S43/)。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **FAIL+GAP** |
| 三层率 | **16 / 4 / 0**（现行） |
| Detector | `token_repeat` + `logits_finite`（均 miss）；**乱码检测漏检** |
| Origin | `both`（constructed wrong-topk-direction） |
| 模型 | Qwen3-8B；**temp=0.8**（勿用 0） |
| Run | 按配方复现（双树 + temp=0.8） |

## 1 · 现象

**各不相同（unique）** 的混合脚本垃圾文字；采样前分值始终有限，没有 NaN/Inf。内容相同计分会低估——`precision=4` **不能单独**当成「几乎没有坏输出」。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 根因

top-k / top-p 作用在 `-logits` 上再取反——保留最低-k / 倒置 nucleus。**不是**放大器。

## 3 · Guard 结果

**FAIL+GAP。** detect=0。异常已出现，但乱码检测漏检。勿用 amplifier-retune 刷检。

## 4 · 复现与双树写入（必读）

本案例 overlay 同时改：

1. Ascend `vllm_ascend/platform.py`（boot 日志）  
2. **vLLM** `vllm/v1/worker/gpu/sample/sampler.py`（真正 flip）

因此：

- **正确：** `gen_s45_overlay.py` 分别写 **Ascend B** + **canonical/vllm**；**temp=0.8**。  
- **错误：** 只 `git apply` 到 Ascend B → `sampler.py: No such file or directory`；或 temp=0。

按配方（双树 + temp=0.8）→ **16 / 4 / 0**（仍为 detect=0，与归档 GAP 一致）。

## 5 · 教学要点

1. 各不相同的有限乱码 + detect=0 → FAIL+GAP；对照 S43（magnitude 故障能检）。
2. 乱码样板对照 **S07**（跨请求相同）；**S01** 是 dense 未见坏输出的对照，不是乱码样板。
3. 环境：必须 **双树写入 + temp=0.8**。
