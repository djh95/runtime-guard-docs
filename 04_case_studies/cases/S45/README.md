# S45 · Top-k on −logits → unique garbage（GAP）

公开自洽案例包。能检对照：[S43](../S43/)。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **FAIL+GAP** |
| 三层率 | **16 / unique(~47/48) / 0** |
| Detector | `token_repeat` + `logits_finite`（均 miss） |
| Origin | `both`（constructed wrong-topk-direction） |
| 模型 | Qwen3-8B |
| Run | 离线归档 archive（WHY + samples） |

## 1 · 现象

**各不相同（unique）** 的混合脚本垃圾文字；logits（采样前的分值）始终是有限数，没有 NaN/Inf。identical-mode 会低估——`layers.json` 里 `precision=0` **不能单独**当成「没有 precision」。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 根因

top-k / top-p 作用在 `-logits` 上再取反——保留最低-k / 倒置 nucleus。**不是**放大器。

## 3 · Guard 结果

**FAIL+GAP。** detect=0。诚实标注；不要标 INVALID，也不要用 amplifier-retune 刷检。

## 4 · 复现与双树写入（必读）

本案例 overlay 同时改：

1. Ascend `vllm_ascend/platform.py`（boot 日志）  
2. **vLLM** `vllm/v1/worker/gpu/sample/sampler.py`（真正 flip）

因此：

- **正确（160）：** `gen_s45_overlay.py` 分别写 B + `canonical/vllm`。  
- **错误：** 只 `git apply` 到 Ascend B → `sampler.py: No such file or directory`。

score：`garbage_mixed_script`×44；`precision_hits≈47`；unique=48。layers identical-mode 会 undercount。

## 5 · 学完能做什么

第三种漏检形态：各不相同的乱码，且 logits（采样前的分值）始终有限、无 NaN/Inf（相对 S01/S07 的跨请求相同乱码）。对照 S43 PASS。环境上记住：**必须双树写入**。
