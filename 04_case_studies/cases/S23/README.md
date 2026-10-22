# S23 · Weight layer zero（PASS · 检出停点（不定界到权重元素））

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
| 三层率 | **2 / 17 / 48** |
| Detector | `token_repeat` |
| Origin | `both`（constructed weight-fault） |
| Guard pin | G2 · `f2aefd068c4bd299d91cf0a1fdf642a3f327308f` |
| 模型 | Qwen3-8B layer=15 o_proj |
| Run | 23_weight_layer_corrupt-20261017T104359 @ builder 机 cards 10,11 |

> **口径：** trigger=2 是 boot 时 `ANOMALY_TRIGGER`（TP2 每卡一次置零），不是「每请求触发」；precision / detect 按请求计，故可出现 **precision > trigger**。结案以 **detect=48** 为准。

## 1 · 现象

跨请求内容相同塌缩×17；`token_repeat`×48。

## 2 · 根因

`load_model` 之后置零一层 `o_proj.weight`（always-on）。不是 NaN / token-fill 放大器，也不是 KV / slot / sampler 族。

## 3 · Guard 结果

**PASS。** 能检出（detect 48），但 skills **不定界到具体权重元素**——教学点是停在检出，不到权重元素细拆。

## 4 · 复现技巧

Qwen3-8B，temp=0，eager；concurrent 48；util=0.40。

## 5 · 教学要点

能检不等于能定界到权重元素。写清已检出即可，不要夸大 dump 能力。

## 定界分析

### 事实

- 现象：跨请求内容相同塌缩（`evidence/samples/`）。
- 三层：2 / 17 / 48；detector：`token_repeat`×48。
- 归档 report：`prompt_token_ids` 为空；有 `output_token_ids`。
- 尚未做 KV 对比（未抓标杆/异常 KV 或未写入本包）。

### 推断

- 可确认：塌缩异常已出现，且 `token_repeat` 已检出。
- 坏输出推不出具体权重地址 / 「一层 o_proj 置零」——构造见「根因」；本案例教学为 detect-only。
- 无对账事实 → 推不出污染时机。

### 结论

- 已定界到：异常输出 + `token_repeat` 检出；不定界到权重元素。
- 尚未定界到具体权重元素；分析不出 / 证据不足。

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
| （constructed weight-fault） | 无单一上游「修复 PR」；教学用权重置零 |
