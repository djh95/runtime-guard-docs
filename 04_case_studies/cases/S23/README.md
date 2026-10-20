# S23 · Weight layer zero（PASS · L1-only）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
| 三层率 | **2 / 17 / 48** |
| Detector | `token_repeat` |
| Origin | `both`（constructed weight-fault） |
| 模型 | Qwen3-8B layer=15 o_proj |
| Run | 23_weight_layer_corrupt-20261017T104359 @ 160 cards 10,11 |

## 1 · 现象

identical-mode collapse×17；`token_repeat`×48。

## 2 · 根因

`load_model` 之后置零一层 `o_proj.weight`（always-on）。不是 NaN / token-fill 放大器，也不是 KV / slot / sampler 族。

## 3 · Guard 结果

**PASS。** 能检出（detect 48），但 skills **不定界到具体权重元素**——教学点是 **L1-only**。

## 4 · 复现

Qwen3-8B，temp=0，eager；concurrent 48；util=0.40。

## 5 · 学完能做什么

能检不等于能定界到权重元素。报 L1 即可，不要夸大 dump 能力。
