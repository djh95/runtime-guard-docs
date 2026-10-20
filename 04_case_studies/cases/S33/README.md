# S33 · Incomplete softcap（PASS）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
| 三层率 | **132 / 15 / 48** |
| Detector | `token_repeat` |
| Origin | `both`（constructed softcap class） |
| 模型 | Qwen3-8B |
| Run | 离线归档；layers 132/15/48 |

## 1 · 现象

`1.1.1…` 模式；`token_repeat`×48。

## 2 · 根因

做了 `÷cap + tanh`，却 **跳过 `*cap` rescale**；boot 强制 cap=30。不等于 S20 的 overflow / `!!!!`。上游族：[vLLM#56579](https://github.com/vllm-project/vllm/pull/56579)。

## 3 · Guard 结果

**PASS。** 归档 **132 / 15 / 48**。

## 4 · 复现与双树写入（必读）

softcap 改在 **vLLM** 的 `logits_processor.py`，同时 Ascend `platform.py` 也要打 boot/trigger。因此：

- **正确（160）：** 跑 `gen_s33_overlay.py`——分别写入 **Ascend B** 与 **canonical vllm**。
- **错误（162 曾 PATCH_FAIL）：** 只对 Ascend B 做 `git apply` → 报 `vllm/model_executor/layers/logits_processor.py: No such file or directory`。

可用 `scripts/apply_anomaly_overlay.sh` 识别双树 patch，但 **仍推荐 gen_***。不要假设「只打 Ascend 就够」。

短例文件名里可能带 overflow 字样；本包以本包归档的 **incomplete softcap** 为准（不是 S20）。

## 5 · 别人按包能核对什么

softcap 族要写清 incomplete 与 unstable overflow 的差别，避免和 S20 混谈。环境构造上记住：**双树写入**。
