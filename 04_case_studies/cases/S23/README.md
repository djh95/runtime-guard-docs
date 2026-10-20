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

**PASS。** 能检出（detect 48），但 skills **不定界到具体权重元素**——教学点是 **L1-only**（停在检测停点，不到问题类细拆）。

## 4 · 复现技巧

Qwen3-8B，temp=0，eager；concurrent 48；util=0.40。

## 5 · 教学要点

能检不等于能定界到权重元素。报 **L1（检测停点）** 即可，不要夸大 dump 能力。

## 定界分析

（**L1** = 检测停点 / **L2** = 问题类停点；**不是** Transformer 层号。见 [④ 名词表 · L1/L2](../../README.md#名词怎么读先看这里)。）

1. **现象与证据**——detector：`token_repeat` 命中（detect=48）。现象见 `evidence/samples/` · `evidence/reports/`（跨请求内容相同塌缩）。归档 report prompt 为空（合修前旧归档；见名词表 **report 空 prompt**，非「clear 过早」）。
2. **排除（应做）**——教学设计为 detect-only，不定界到权重元素；KV 排除路径仍可用（重放抓 ids + 标杆/异常 KV），但**非本案细定界目标**。**本案归档尚未附 KV 对比结论**。
3. **定界结论**——停在 **L1（检测停点）**：仅检出（权重 corruption · detect-only，不定界到权重元素）。不宣称 **L2（问题类）** 细拆。结案：PASS；constructed always-on（post-load 置零一层 o_proj）。

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
| （constructed weight-fault） | 无单一上游「修复 PR」；教学用 L1 权重置零 |
