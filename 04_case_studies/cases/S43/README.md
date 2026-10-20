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

## 4 · 复现

对照 S45：同属 embed/logits 族，一边 PASS，一边 unique-garbage GAP。

## 5 · 别人按包能核对什么

能检的 magnitude 故障，和漏检的方向翻转采样，适合成对看。
