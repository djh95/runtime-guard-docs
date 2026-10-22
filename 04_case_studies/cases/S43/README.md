# S43 · Embed ×100 → newline collapse（PASS）

公开自洽案例包。漏检对照：[S45](../S45/)。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
| 三层率 | **16 / 40 / 48** |
| Detector | `token_repeat` |
| Origin | `both`（constructed） |
| Guard pin | G2 · `f2aefd068c4bd299d91cf0a1fdf642a3f327308f` |
| Run | 43_embed_scale_blowup-20261017T153923 @ builder 机 cards 10,11 |

## 1 · 现象

大量换行塌缩；`token_repeat`×48。

## 2 · 根因

`AscendVocabParallelEmbedding` lookup 后 `mul_(100)`。不等于 S23 weight-zero，也不等于 S41 attn-out。

## 3 · Guard 结果

**PASS。** **16 / 40 / 48**。score 需认 `newline_collapse`——只数裸 `.` 会 miss `\n`。

## 4 · 复现技巧

对照 S45：同属 embed/logits 族，一边 PASS，一边 unique-garbage GAP。

## 5 · 教学要点

与 S45 成对看：本包是 magnitude 放大能检；S45 是采样方向翻转 → 各不相同乱码漏检。

## 定界分析

### 事实

- 现象：换行塌缩（`evidence/samples/`）。
- 三层：16 / 40 / 48；detector：`token_repeat`×48。
- 归档 report：`prompt_token_ids` 为空；有 `output_token_ids`。
- 尚未做 KV 对比（未抓标杆/异常 KV 或未写入本包）。

### 推断

- 可确认：塌缩异常已出现，且 `token_repeat` 已检出。
- 坏输出推不出「embed ×100」——构造见「根因」。
- 无对账事实 → 推不出污染时机。

### 结论

- 已定界到：塌缩异常 + `token_repeat` 检出。
- 尚未定界到 embed ×100；分析不出 / 证据不足。

## 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格（Origin / 锚点 / overlay / knobs / 期望 detector） |
| `evidence/三层计数.json` | 三层明细（trigger / precision / detect） |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/samples/` | prompt + completion 样本 |
| `evidence/reports/` | Guard detector 报告（归档 report prompt 为空：合修前旧归档，见名词表 **report 空 prompt**；可读 prompt 看 samples，见 [④ 名词表](../../README.md#名词怎么读先看这里)） |


## 上游 PR 关系

| PR / 链接 | 角色 |
|-----------|------|
| （constructed embed×100） | 无单一上游修复 PR；与 S45 成对教学 |
