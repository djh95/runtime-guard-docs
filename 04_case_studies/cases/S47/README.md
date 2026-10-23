# S47 · Attn K/V swap（KV 不一致→定界）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 不一致→定界** |
| 检测 | **检出** |
| 三层率 | **30 / 0（计数）· identical-mode 垃圾×37 / 48**（`token_repeat`×48） |
| Detector | `token_repeat` |
| Origin | 见规格 |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) |
| 模型 | Qwen3-8B · TP2 · CARD=4,5 · `192.168.13.160` / `rg-test-160` |
| Run | `keep-set-retest-20261022` · `S47-layers-20261023T111450` / `S47-pr19285-20261023T111625` |

## 1 · 现象

乱码/重复字串（`precision_identical_mode`×37；计数器 `precision=0`）。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 案例背景 / 构造

Attention 前 K/V 对调。细节见 [evidence/规格说明.md](./evidence/规格说明.md)。**构造根因不是本包 KV 定界已证。**

## 3 · Guard 结果

**检出。** trigger=30；detect=`token_repeat`×48。结案档：**KV 不一致→定界**（v5.16：无数值问题；余弦自 token0 / L0 起不一致）。

## 4 · 复现技巧

| 项 | 现行复现 |
|----|----------|
| Overlay | `gen_s47_overlay.py` |
| 并发 | 48 |
| detector | `token_repeat` |
| 抓 dump | #19285；抓前清 `kv_cache` |
| 标杆 | 清洁树；force-feed history |

## 5 · 定界分析

### 事实

- **≥2 组**清洁标杆；shape 一致。
- **v5.16（两对同向）：** 数值问题格 **0**。

| 对 | first_numeric | first_cos（model.layers） | worst @token0 |
|----|---------------|---------------------------|---------------|
| `…91bc86cf` | 无 | token **0** @ `model.layers.0`（cos≈0.008） | `model.layers.8`（≈-0.15） |
| `…b83b5dc7` | 无 | token **0** @ `model.layers.0`（cos≈0.008） | `model.layers.8`（≈-0.15） |

- 未用槽：异常侧有限非 0（卫生）；标杆未用全 0。
- 证据：`evidence/kv_compare.json` + `kv_v516_numeric_first.json`；`verified_kv/S47/ref_recap/`（**.pt 未入库**）。

### 推断

- prompt token0 起全层余弦已崩 → **KV 不一致**；符合 K/V 对调类构造的早期发散，**但非已证根因**。

### 结论

- 结案档：**KV 不一致→定界**（两组同向）。

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
