# S43 · Embed ×100 → newline collapse（PASS）

公开自洽案例包。漏检对照：[S45](../S45/)。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
| 三层率 | **16 / 40 / 48** |
| Detector | `token_repeat` |
| Origin | `both`（constructed） |
| Run | 43_embed_scale_blowup-20261017T153923 @ 160 cards 10,11 |

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

## 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/status.json` | 结案摘要 |
| `evidence/layers.json` | 三层明细 |
| `evidence/samples/` | 样本 |
| `evidence/reports/` | token_repeat report |
| `evidence/overlay.patch` | overlay |
| `evidence/runtime_config.json` | 运行配置 |
| `evidence/SPEC_excerpt.md` | SPEC 摘录 |
| `evidence/WHY_PASS.md` | 为何 PASS |

## 上游 PR 关系

| PR / 链接 | 角色 |
|-----------|------|
| （constructed embed×100） | 无单一上游修复 PR；与 S45 成对教学 |
