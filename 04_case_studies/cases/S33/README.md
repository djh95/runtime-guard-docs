# S33 · Incomplete softcap（KV 一致→排除 KV）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 一致→排除 KV** |
| 检测 | **检出** |
| 三层率 | **102 / 15 / 48**（`token_repeat`×48） |
| Detector | `token_repeat` |
| Origin | 见规格 |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) |
| 模型 | Qwen3-8B · TP2 · CARD=4,5 · `192.168.13.160` / `rg-test-160` |
| Run | `keep-set-retest-20261022` · `S33-layers-20261023T112336` |

## 1 · 现象

部分数字 / token 复读（precision=15）；`token_repeat` 检出。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 案例背景 / 构造

softcap 缺 `*cap` rescale。细节见 [evidence/规格说明.md](./evidence/规格说明.md)。**构造背景不是本包 KV 已证根因。**

## 3 · Guard 结果

**检出。** **102 / 15 / 48**。结案档：**KV 一致→排除 KV**（v5.16：有效槽有限、无数值问题；干净格余弦全程 ≥0.99）。

## 4 · 复现技巧

| 项 | 现行复现 |
|----|----------|
| Overlay | `gen_s33_overlay.py` |
| 并发 | 48 |
| detector | `token_repeat` |
| 抓 dump | #19285；抓前清 `kv_cache` |
| 标杆 | 清洁树；force-feed history |

## 5 · 定界分析

### 事实

- **清洁标杆（≥2 组）：** 干净服务重放对照；**2 组**；shape 一致。对比窗约 `n_prompt=14`，`p+o−1`≈20。
- **两对同向：** 数值问题格 **0**；余弦全程干净（prompt 第 1 个 token 最差仍≈1.0）。
- **未用槽：** 异常侧有限非 0（**卫生**）。
- 证据：`evidence/kv_*.json`（**.pt 未入库**）。

### 推断

- 有效对账匹配 → **排除「坏值经/进 KV」为主因路径**（就本窗、本 head、matched 层而言）。
- 异常仍检出 → 问题更可能在采样/logits 后处理等 **非本包 KV 对比覆盖** 路径；**不能**从 KV 推出 softcap 根因。

### 结论

- 结案档：**KV 一致→排除 KV**（两组同向；标杆洁净）。
- 未用槽有限脏写仅附注卫生。

## 6 · 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 补丁 |
| `evidence/规格说明.md` | 规格 |
| `evidence/三层计数.json` | 三层 |
| `evidence/跑批结果.json` | 摘要 |
| `evidence/samples/` | 样本 |
| `evidence/reports/` | report |
| `evidence/kv_compare.json` | v5.16 摘要 |
| `evidence/kv_v516_numeric_first.json` | 明细 |
| `evidence/kv_finite_unused.json` | 有限性/未用槽 |
| `evidence/kv_pairs_recap.json` | 配对 |

## 7 · 上游 PR 关系

| 链接 | 角色 |
|------|------|
| （构造；见规格） | 背景 |
| [ascend#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) | 抓 dump 辅助 |
