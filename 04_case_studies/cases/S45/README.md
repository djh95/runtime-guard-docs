# S45 · Top-k on −logits → unique garbage（KV 一致→排除 KV · 乱码漏检）

公开自洽案例包。能检对照：[S43](../S43/)。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 一致→排除 KV** |
| 检测 | **乱码漏检** |
| 三层率 | **16 / 4 / 0**（现行；trigger/precision 随并发浮动，detect 为判定口径） |
| Detector | `token_repeat` + `logits_finite`（均 miss）；**乱码检测漏检** |
| Origin | `both`（constructed wrong-topk-direction） |
| Guard pin | G2 · `f2aefd068c4bd299d91cf0a1fdf642a3f327308f` |
| 模型 | Qwen3-8B；**temp=0.8**（勿用 0） |
| Run | 按复现技巧复现（双树 + temp=0.8） |

## 1 · 现象

**各不相同（unique）** 的混合脚本垃圾文字；采样前分值始终有限，没有 NaN/Inf。内容相同计分会低估——`precision=4` **不能单独**当成「几乎没有坏输出」。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 根因

top-k / top-p 作用在 `-logits` 上再取反——保留最低-k / 倒置 nucleus（构造故障本身；不是靠伪造 NaN/填复读 token 硬造症状）。

## 3 · Guard 结果

**乱码漏检。** detect=0。异常已出现，detector 未命中；manual dump 已完成有效对账。结案档：**KV 一致→排除 KV**。

## 4 · 复现技巧与双树写入（必读）

本案例 overlay 同时改：

1. Ascend `vllm_ascend/platform.py`（boot 日志） 
2. **vLLM** `vllm/v1/worker/gpu/sample/sampler.py`（真正 flip）

因此：

- **正确：** `gen_s45_overlay.py` 分别写 **Ascend B** + **canonical/vllm**；**temp=0.8**。 
- **错误：** 只 `git apply` 到 Ascend B → `sampler.py: No such file or directory`；或 temp=0。

按复现技巧（双树 + temp=0.8）→ **16 / 4 / 0**（仍为 detect=0，乱码漏检）。

## 定界分析

### 事实

- detect=0（乱码检测漏检）→ 归档 anomaly-repro 无 detector 触发的 `*.pt`；本轮用 **manual_dump** 重抓异常侧 KV 后完成对账（见 `evidence/kv_compare.json`）。
- 本包已归档 KV 对比（cos_thresh=0.99；n_prompt=14 n_cmp_tokens=14；matched_layers=72）。
- 标杆 vs 异常：对比窗口内**全程一致**（min-over-layers cos = 1.0）；首不一致：无。
- 对比窗 caveat：manual_dump 早拍，report `output_token_ids` 仅 o=1 → history 窗=**prompt only**（无 out0 余弦）。

### 推断

- 对账一致 → **排除 KV cache** 作为本请求坏输出的必要原因（转向采样/非 KV 类；与 top-k 打在 −logits 的构造预期一致）。
- 坏输出仍不能从文本推出构造根因。
- 无首不一致 → 推不出「prefill 中途 / 传写 / decode 前」等污染时机窗口。
- o=1 早拍使 output 槽位未入窗；排除力度以 prompt 窗为准，不把「全序列 output KV 已验」写死。

### 结论

- 结案档：**KV 一致→排除 KV**（本请求 prompt 对比窗口）。
- 尚未定界到具体算子/构造根因；分析不出 / 证据不足。

## 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格（Origin / 锚点 / overlay / knobs / 期望 detector） |
| `evidence/三层计数.json` | 三层明细（trigger / precision / detect） |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/kv_compare.json` | 最新 KV 标杆对比摘要（余弦 / 首不一致 / 结论） |
| `evidence/samples/` | prompt + completion 样本 |

## 上游 PR 关系

| PR / 链接 | 角色 |
|-----------|------|
| （constructed wrong-topk-direction） | 无单一上游修复 PR；对照能检侧见 S43 |
