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

1. **L1 detect 停点**——detect=0：`token_repeat`+`logits_finite` 均 miss → **乱码检测漏检**。
2. **L2 class-hint**——弱 L2——各不相同有限乱码（unique-garbage）。
3. **标杆 / Q1–Q5（KV 排除）**——空 prompt / 包内暂无 buggy+ref **不等于**「Q1–Q5 不适用」。有 report 即可：同 prompt 再 curl 抓服务端 `prompt_token_ids`，与异常 `output_token_ids` 合并后抓标杆 KV，对比异常 KV（一致→排除 KV；不一致→重开 KV 线）。**本案归档尚未附 KV 对比结论**；现行对外结案停在 L1+L2+现象。
4. **结合现象**——见 `evidence/samples/`。
5. **结案要点**——FAIL+GAP：异常已出现；双树 + temp=0.8 → 16/4/0。

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
