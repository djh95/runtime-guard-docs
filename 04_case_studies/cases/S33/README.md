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

### 事实

- 现象：`1.1.1…` 复读（`evidence/samples/`）。
- 三层：130 / 17 / 48；detector：`token_repeat`×48。
- 归档 report：`prompt_token_ids` 非空（len=14）；有 `output_token_ids`。
- 尚未做 KV 对比（未抓标杆/异常 KV 或未写入本包）。

### 推断

- 可确认：复读异常已出现，且 `token_repeat` 已检出。
- 坏输出推不出「softcap 缺 *cap rescale」——构造见「根因」。
- 无对账事实 → 推不出污染时机；勿因缺 buggy+ref 写「Q1–Q5 不适用」。

### 结论

- 已定界到：复读异常 + `token_repeat` 检出。
- 尚未定界到 softcap rescale；分析不出 / 证据不足。

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
