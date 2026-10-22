# S23 · Weight layer zero（PASS · L1-only）

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

**PASS。** 能检出（detect 48），但 skills **不定界到具体权重元素**——教学点是 **L1-only**（停在检测停点，不到问题类细拆）。

## 4 · 复现技巧

Qwen3-8B，temp=0，eager；concurrent 48；util=0.40。

## 5 · 教学要点

能检不等于能定界到权重元素。报 **L1（检测停点）** 即可，不要夸大 dump 能力。

## 定界分析

### 事实

- 三层：2 / 17 / 48；detector：`token_repeat` 命中（detect=48；`evidence/samples/` · `evidence/reports/`）。
- sample：跨请求内容相同塌缩。
- 归档 report `prompt_token_ids` 为空；有 `output_token_ids`。
- 包内无标杆 vs 异常 KV 对账；教学设计为 detect-only。

### 推断

- 可确认：塌缩异常且 `token_repeat` 已检出。
- 教学目标不定界到权重元素；坏输出推不出具体权重地址。
- KV 排除路径可用但非本案例细定界目标；包内未附对账。

### 结论

- 已定界到：异常输出 + `token_repeat` 检出；不定界到权重元素。
- **尚未定界到** 具体权重元素；**分析不出 / 证据不足**（detect-only）。
- KV：路径可用；归档尚未附结论。
- **定界结论：L1** = `token_repeat` 已命中；**L2** = 不宣称（detect-only）。
- 结案：PASS。


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
