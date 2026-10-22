# S43 · Embed ×100 → newline collapse（KV 不一致→定界）

公开自洽案例包。漏检对照：[S45](../S45/)。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 不一致→定界** |
| 检测 | **检出** |
| 三层率 | **16 / 40 / 48** |
| Detector | `token_repeat` |
| Origin | `both`（constructed） |
| Guard pin | G2 · `f2aefd068c4bd299d91cf0a1fdf642a3f327308f` |
| Run | 43_embed_scale_blowup-20261017T153923|

## 1 · 现象

大量换行塌缩；`token_repeat`×48。

## 2 · 根因

`AscendVocabParallelEmbedding` lookup 后 `mul_(100)`。不等于 S23 weight-zero，也不等于 S41 attn-out。

## 3 · Guard 结果

**检出。** **16 / 40 / 48**。score 需认 `newline_collapse`——只数裸 `.` 会 miss `\n`。结案档：**KV 不一致→定界**。

## 4 · 复现技巧

对照 S45：同属 embed/logits 族；本包检出，S45 乱码漏检（但 S45 结案为 KV 一致→排除 KV）。

## 定界分析

### 事实

- 现象：换行塌缩 / 复读（`evidence/samples/`）。
- 三层见包内计数；detector：`token_repeat`。
- 本包已归档 KV 对比（cos_thresh=0.99；n_prompt=14 n_cmp_tokens=18；layers=72）。
- 首不一致：idx=0 role=prompt span=prompt min_cos=-0.295200 @ model.layers.20.self_attn.attn。
- 后续是否恢复≈1：False；output 首 token 余弦=-0.237587；仅 PD：False。

### 推断

- 对账不一致 → **重开 KV 线**。
- 坏输出仍不可直接写成具体根因。
- 首不一致在 prompt 段 → 偏向 prefill 侧（需结合是否恢复、仅 PD）。

### 结论

- 结案档：**KV 不一致→定界**（重开 KV 线）。
- 尚未定界到具体写/传路径；分析不出 / 证据不足。

## 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格（Origin / 锚点 / overlay / knobs / 期望 detector） |
| `evidence/三层计数.json` | 三层明细（trigger / precision / detect） |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/samples/` | prompt + completion 样本 |
| `evidence/reports/` | Guard detector 报告 |
| `evidence/kv_compare.json` | 最新 KV 标杆对比摘要（余弦 / 首不一致 / 结论） |

## 上游 PR 关系

| PR / 链接 | 角色 |
|-----------|------|
| （constructed embed×100） | 无单一上游修复 PR；与 S45 成对教学 |
