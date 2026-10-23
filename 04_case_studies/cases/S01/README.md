# S01 · 新 KV block 未置零（KV 一致→排除 KV）

公开自洽案例包。本轮在 **dense Qwen3-8B** 上实测（规格写 hybrid/量化形态前提；本轮未用 hybrid 权重）。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 一致→排除 KV** |
| 检测 | **检出** |
| 三层率 | **82 / 16 / 48**（`token_repeat`×48） |
| Detector | `token_repeat` |
| Origin | 见规格 |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) |
| 模型 | Qwen3-8B dense · TP2 · CARD=4,5 · `192.168.13.160` / `rg-test-160` |
| Run | `keep-set-retest-20261022` · `S01-layers-20261023T125812` |

## 1 · 现象

检出 `token_repeat`（precision=16；如 `1.1.1.1…` 重复）。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 案例背景 / 构造

新 KV block 未置零。细节见 [evidence/规格说明.md](./evidence/规格说明.md)。**规格 hybrid/量化前提本轮未满足；结论仅对 dense 本窗有效。**

## 3 · Guard 结果

**检出。** **82 / 16 / 48**。结案档：**KV 一致→排除 KV**（v5.16：无数值问题；余弦全程 clean）。

## 4 · 复现技巧

| 项 | 现行复现 |
|----|----------|
| Overlay | `01_kv_block_nonzero.patch` |
| 模型 | Qwen3-8B dense（本轮） |
| 负载 | pad churn · concurrency 48 |
| detector | `token_repeat` |

## 5 · 定界分析

### 事实

- **≥2 组**清洁标杆；shape 一致。
- **v5.16（两对同向）：** 数值问题格 **0**；`first_cos_mismatch` **无**（全程 clean）。
- 未用槽：异常侧有限非 0（卫生）。
- 证据：`evidence/kv_*.json`（**.pt 未入库**）。

### 推断

- 有效对账匹配 → **排除「坏值经/进 KV」为主因路径**（dense 本窗）。
- 不把本轮结果推广为 hybrid/量化形态下的定界。

### 结论

- 结案档：**KV 一致→排除 KV**（dense；两组同向）。

## 6 · 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 补丁 |
| `evidence/规格说明.md` | 规格 + 实测 |
| `evidence/三层计数.json` / `跑批结果.json` | 三层 / 摘要 |
| `evidence/samples/` / `reports/` | 样本 / 报告 |
| `evidence/kv_*.json` | 对账 |

## 7 · 上游 PR 关系

见规格（#43990 / #47574）。
