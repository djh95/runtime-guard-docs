# S33 · softcap 不完整（KV 一致→排除 KV）

公开案例包。logits softcap 少做了一步缩放（`*cap`）。输出出现数字/token 复读并被检出；KV 对账干净 → **排除 KV 主因**。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 一致→排除 KV** |
| 检测 | **检出** |
| 三层率 | **102 / 15 / 48**（触发 / 判坏 / 报告） |
| Detector | `token_repeat` |
| Origin | 见规格 |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) |
| 模型 | 见规格 / 跑批 |
| Run | `keep-set-retest-20261022` · `S33-layers-20261023T112336` |

## 1 · 现象

部分数字 / token 复读（约 15/48）；重复检测命中。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 案例背景 / 构造

softcap 缺 `*cap` rescale。细节见 [evidence/规格说明.md](./evidence/规格说明.md)。**注意双树**：只改 Ascend、不改上游 vLLM 采样侧时，补丁可能 apply 失败。

## 3 · Guard 结果

**检出。** **102 / 15 / 48**。结案：**KV 一致→排除 KV**——有效槽有限、无数值崩溃；相似度全程 ≥0.99（见事实）。

## 4 · 复现技巧

| 项 | 怎么做 |
|----|--------|
| Overlay | 见规格（常需动 Ascend + vLLM 两侧） |
| detector | `token_repeat` |
| 对照 | 干净树上按 token id 原样重放 |

## 5 · 定界分析

### 事实

- **清洁标杆（≥2 组）：** 干净服务重放对照；**2 组**；shape 一致。对比窗约 `n_prompt=14`，`p+o−1`≈20。
- **两对同向：** 数值问题格 **0**；余弦全程干净（prompt 第 1 个 token 最差仍≈1.0）。
- **未用槽：** 异常侧有限非 0（**卫生**）。
- 证据：`evidence/kv_*.json`（**.pt 未入库**）。

### 推断

- 对账匹配 → **排除 KV 主因**（本窗）。
- 复读更贴近 logits softcap 路径，而非已匹配的 KV 槽。

### 结论

- 结案档：**KV 一致→排除 KV**。

## 6 · 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 补丁 |
| `evidence/规格说明.md` | 规格 + 实测 |
| `evidence/三层计数.json` / `跑批结果.json` | 三层 / 摘要 |
| `evidence/samples/` / `reports/` | 样本 / 报告 |
| `evidence/kv_*.json` | 对账 |

## 7 · 上游 PR 关系

见规格。
