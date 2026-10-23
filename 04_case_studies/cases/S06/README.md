# S06 · MoE 路由 bias（KV 不一致→定界）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 不一致→定界** |
| 检测 | **检出** |
| 三层率 | **52 / 25 / 46**（`token_repeat`×46；n_req=48） |
| Detector | `token_repeat` |
| Origin | 见规格 |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) |
| 模型 | DeepSeek-V2-Lite · TP2 · CARD=4,5 · `192.168.13.160` / `rg-test-160` |
| Run | `keep-set-retest-20261022` · `S06-layers-20261023T122714` |

## 1 · 现象

检出 `token_repeat`（precision=25）。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 案例背景 / 构造

MoE router bias / mask 错误。细节见 [evidence/规格说明.md](./evidence/规格说明.md)。**构造背景不是本包 KV 已证根因名。**

## 3 · Guard 结果

**检出。** **52 / 25 / 46**。结案档：**KV 不一致→定界**（v5.16：无数值问题；首个余弦分歧约在 dump `layer_27`，模型侧约第 4 层；两组同向）。

## 4 · 复现技巧

| 项 | 现行复现 |
|----|----------|
| Overlay | `06_moe_routing_bias.patch` |
| 模型 | DeepSeek-V2-Lite（MoE） |
| detector | `token_repeat` |
| 抓 dump | #19285；双树 checkout |
| 标杆 | 清洁树；force-feed history |

## 5 · 定界分析

### 事实

- **≥2 组**清洁标杆；shape 一致。
- **v5.16（两对同向）：** 无数值问题；prompt 第 1 个 token 上 dump `layer_27` 余弦≈0.05；模型层首分歧约在 `model.layers.4`（余弦≈0.85）。
- 未用槽：异常侧有限非 0（卫生）。
- 证据：`evidence/kv_compare.json` + `kv_v516_numeric_first.json`（**.pt 未入库**）。

### 推断

- 有效槽余弦已分 → **定界到本窗首分歧层**（见上）；**不**把分歧自动等同 MoE 路由源码行。

### 结论

- 结案档：**KV 不一致→定界**（两组同向）。

## 6 · 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 补丁 |
| `evidence/规格说明.md` | 规格 + 实测状态 |
| `evidence/三层计数.json` | 三层 |
| `evidence/跑批结果.json` | 跑批摘要 |
| `evidence/samples/` | 样本 |
| `evidence/reports/` | detector 报告 |
| `evidence/kv_compare.json` | 对账摘要 |
| `evidence/kv_v516_numeric_first.json` | v5.16 |
| `evidence/kv_finite_unused.json` | 有限性/未用槽 |
| `evidence/kv_pairs_recap.json` | 成对路径 |

## 7 · 上游 PR 关系

见规格（#38989 / #60946）。
