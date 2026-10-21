# S33 · Incomplete softcap（PASS）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
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

**PASS。** 现行 **130 / 17 / 48**。

## 4 · 复现技巧与双树写入（必读）

softcap 改在 **vLLM** 的 `logits_processor.py`，同时 Ascend `platform.py` 也要打 boot/trigger。因此：

- **正确：** 跑 `gen_s33_overlay.py`——分别写入 **Ascend B** 与 **canonical vllm**。  
- **负载：** 与 S25/S26 同族——英文河名短句 ×**48 并发**（勿用中文回声串行）。

只对 Ascend B 做 `git apply`（缺 vLLM 树）会 PATCH_FAIL；中文回声串行打不出 `1.1.1…`。

可用 `scripts/apply_anomaly_overlay.sh` 识别双树 patch，但 **仍推荐 gen_***。

本包以归档的 **incomplete softcap** 为准（不是 S20 overflow）。

## 5 · 教学要点

softcap 族要写清 incomplete 与 unstable overflow 的差别，避免和 S20 混谈。环境：**双树写入 + 河名句并发**。

## 定界分析

（**L1** = 检测停点 / **L2** = 问题类停点；**不是** Transformer 层号。见 [④ 名词表 · L1/L2](../../README.md#名词怎么读先看这里)。）

1. **现象与证据**——detector：`token_repeat`×48。现象见 `evidence/samples/` · `evidence/reports/`。
2. **排除（应做）**——空 prompt / 包内暂无 buggy+ref **不等于**「Q1–Q5 不适用」。有 report 即可：同 prompt 再 curl 抓服务端 `prompt_token_ids`，与异常 `output_token_ids` 合并后抓标杆 KV，对比异常 KV（一致→排除 KV；不一致→重开 KV 线）。**本案例归档尚未附 KV 对比结论**。
3. **定界结论**——停在 **L2（问题类停点）**：softcap 缺 `*cap` rescale；≠S20 overflow/`!!!!`。**L1（检测停点）**：`token_repeat` 已命中。结案：PASS **130 / 17 / 48**；须双树写入。

## 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格（Origin / 锚点 / overlay / knobs / 期望 detector） |
| `evidence/三层计数.json` | 三层明细（trigger / precision / detect） |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/samples/` | prompt + completion 样本 |
| `evidence/reports/` | Guard detector 报告 |


## 上游 PR 关系

| PR / 链接 | 角色 |
|-----------|------|
| [vLLM#56579](https://github.com/vllm-project/vllm/pull/56579) | **同族相关**（softcap）；本包为 incomplete rescale 构造 |
