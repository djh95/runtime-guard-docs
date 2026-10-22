# S23 · Weight layer zero（复现未抓到）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **复现未抓到** |
| 检测 | **检出** |
| 三层率 | **2 / 17 / 48** |
| Detector | `token_repeat` |
| Origin | `both`（constructed weight-fault） |
| Guard pin | G2 · `f2aefd068c4bd299d91cf0a1fdf642a3f327308f` |
| 模型 | Qwen3-8B layer=15 o_proj |
| Run | 23_weight_layer_corrupt-20261017T104359|

> **口径：** trigger=2 是 boot 时 `ANOMALY_TRIGGER`（TP2 每卡一次置零），不是「每请求触发」；precision / detect 按请求计，故可出现 **precision > trigger**。结案以 **detect=48** 为准。

## 1 · 现象

跨请求内容相同塌缩×17；`token_repeat`×48。

## 2 · 根因

`load_model` 之后置零一层 `o_proj.weight`（always-on）。不是 NaN / token-fill 放大器，也不是 KV / slot / sampler 族。

## 3 · Guard 结果

**检出**（detect 48），但 skills **不定界到具体权重元素**——教学点是停在检出，不到权重元素细拆。结案档：**复现未抓到**。

## 4 · 复现技巧

Qwen3-8B，temp=0，eager；concurrent 48；util=0.40。

## 5 · 定界分析

### 事实

- 现象 / 检测见上文钉点与 samples（或 reports）。
- **有效 KV 对账：无。** 本包曾归档的 `kv_compare.json` 及其中「首不一致 / 层号 / 余弦」结论**全部撤回**（新旧跑次混用、空 prompt、弱窗、全 NaN 占位等问题，不可信）。

### 推断

- 在重做**同一次异常请求**的有效异常 dump ↔ 标杆对账之前，**不能**得出「排除 KV」或「KV 不一致定界」。
- 坏输出 / 构造预期 ≠ 已证根因。

### 结论

- 结案档：**复现未抓到**（有异常或检出证据，但无有效异常 KV 可对账）。
- **尚未做有效 KV 对账**；分析不出 / 证据不足。


## 6 · 证据文件
| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格（Origin / 锚点 / overlay / knobs / 期望 detector） |
| `evidence/三层计数.json` | 三层明细（trigger / precision / detect） |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/samples/` | prompt + completion 样本 |
| `evidence/reports/` | Guard detector 报告 |

## 7 · 上游 PR 关系
| PR / 链接 | 角色 |
|-----------|------|
| （constructed weight-fault） | 无单一上游「修复 PR」；教学用权重置零 |
