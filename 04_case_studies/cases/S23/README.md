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

跨请求内容相同塌缩×17；`token_repeat`×48。

## 2 · 根因

`load_model` 之后置零一层 `o_proj.weight`（always-on）。不是 NaN / token-fill 放大器，也不是 KV / slot / sampler 族。

## 3 · Guard 结果

**PASS。** 能检出（detect 48），但 skills **不定界到具体权重元素**——教学点是 **L1-only**。

## 4 · 复现技巧

Qwen3-8B，temp=0，eager；concurrent 48；util=0.40。

## 5 · 教学要点

能检不等于能定界到权重元素。报 L1 即可，不要夸大 dump 能力。

## 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/status.json` | 跑批元数据 |
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
| （constructed weight-fault） | 无单一上游「修复 PR」；教学用 L1 权重置零 |
