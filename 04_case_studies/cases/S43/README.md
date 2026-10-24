# S43 · Embedding ×100（KV 不一致→定界）

公开案例包。把 embedding 放大 100 倍。输出几乎只剩换行/空白，且多条请求内容相同；重复检测抓住；KV 从 prompt 第 1 个 token 起就和干净对照对不上。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 不一致→定界** |
| 检测 | **检出** |
| 三层率 | **16 / 40 / 48**（触发 / 判坏 / 报告；报告全是 `token_repeat`） |
| Detector | `token_repeat` |
| Origin | 见规格 |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) |
| 模型 | Qwen3-8B · TP2 · CARD=4,5 |
| Run | `keep-set-retest-20261022` · `S43-layers-20261023T104944` / `S43-pr19285-20261023T105118` / `S43-ref-recap-20261023T105259` |

## 1 · 现象

大量「换行塌缩」：输出几乎只剩换行/空白；约 40 条内容相同。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 案例背景 / 构造

embedding 权重 ×100。细节见 [evidence/规格说明.md](./evidence/规格说明.md)。

## 3 · Guard 结果

**检出。** **16 / 40 / 48**。结案：**KV 不一致→定界**——无数值崩溃；从 prompt 第 1 个 token 起相似度就不一致（见事实）。

## 4 · 复现技巧

| 项 | 怎么做 |
|----|--------|
| Overlay | 见规格 / 生成脚本 |
| detector | `token_repeat` |
| 对照 | 干净树上按 token id 原样重放 |

## 5 · 定界分析

### 事实

- **清洁标杆（≥2 组）：** 干净服务重放对照；shape 一致；标杆未用槽归零。history **`p + o − 1 = 18`**（约 prompt=14、生成较短）。
- **两对同向：** 无数值问题；余弦可算，且两对同一套层叙事。
- **余弦：** prompt 第 1 个 token 起，`model.layers.0–1` 仍≈1；自 **`model.layers.2`** 首次明显偏离（余弦≈0.55）；同 token 最差约 −0.30 落在 `model.layers.20`。
- **dump 双名：** 另有 `layer_36…` 一套名字；`layer_36` = `model.layers.0`（`layer_(36+i)` ↔ `model.layers.i`）。全名排序的「首次余弦」可能先写到 `layer_36`，与「模型第 2 层首越阈」是同一对账的不同命名视图。
- **未用槽：** 异常侧有限非 0（**卫生**）。
- 证据：`evidence/kv_*.json`；`verified_kv/S43/`（**.pt 未入库**）。

### 推断

- 相似度从很早的层就开始偏 → **KV 不一致可定界到本窗首分歧**；不定界到「embedding×100」源码行以外的断言。

### 结论

- 结案档：**KV 不一致→定界**（两组同向）。

## 6 · 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 补丁 |
| `evidence/规格说明.md` | 规格 |
| `evidence/三层计数.json` / `跑批结果.json` | 三层 / 摘要 |
| `evidence/samples/` / `reports/` | 样本 / 报告 |
| `evidence/kv_*.json` | 对账 |

## 7 · 上游 PR 关系

见规格。
