# S10′ · FullAttn recycle-zero（KV 一致→排除 KV）

公开自洽案例包。目录名 `S10p` = S10′。构造预期像「回收块脏 KV」，**本窗对账却干净** → 结案排除 KV 主因。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 一致→排除 KV** |
| 检测 | **检出** |
| 三层率 | **64 / 17 / 64**（`token_repeat`×64） |
| Detector | `token_repeat` |
| Origin | 见规格 |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) |
| 模型 | Qwen3-8B · TP2 · CARD=4,5 · util=0.35 · max-num-seqs=128 · `192.168.13.160` / `rg-test-160` |
| Run | `keep-set-retest-20261022` · `S10p-layers-20261023T121734` |

## 1 · 现象

检出 `token_repeat`（precision=17）。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 案例背景 / 构造

FullAttention 回收块未清零（`needs_kv_cache_zeroing→False`）。细节见 [evidence/规格说明.md](./evidence/规格说明.md)。**构造「预期根因在 KV」≠ 本窗已证根因。**

## 3 · Guard 结果

**检出。** **64 / 17 / 64**。结案档：**KV 一致→排除 KV**（v5.16：有效槽有限、无数值问题；干净格余弦全程 ≥0.99）。

## 4 · 复现技巧

| 项 | 现行复现 |
|----|----------|
| Overlay | `10_fullattn_recycle_zero.patch`（或 `gen_s10_overlay.py` 生成） |
| 负载 | pad 变长 prompt · concurrency 64 · temp=0 · churn |
| detector | `token_repeat` |
| 抓 dump | #19285；抓前清双树 |
| 标杆 | 清洁树；force-feed history |

## 5 · 定界分析

### 事实

- **清洁标杆（≥2 组）：** 干净服务重放对照；**2 组**；shape 一致。对比窗口含**完整 prompt+生成**（不是只比了一截）；本窗约 `n_prompt=14`，`p+o−1`≈21。
- **两对同向：** 无数值问题；余弦全程干净（prompt 第 1 个 token 最差仍≈1.0）。
- **有效槽 / 格：** 有效槽有限、无数问题；没有「第一处余弦分叉」。
- **未用槽：** 异常侧有限非 0（**卫生**）；一对标杆未用槽也可能有限非 0——不单独当成坏结果原因。
- **读法：** 构造预期像「回收块脏 KV」，但本窗对账匹配 → 结案是**排除 KV 主因**（就本窗、本 head、对上的层而言）。
- 证据：`evidence/kv_*.json`；`verified_kv/S10p/`（**.pt 未入库**）。

### 推断

- 有效对账匹配 → **排除「坏值经/进 KV」为主因路径**（就本窗、本 head、matched 层而言）。
- 异常仍检出 → 问题更可能在未对比到的路径 / 时序 / 其它块；**不能**仅凭本窗余弦把根因钉在 recycle-zero。

### 结论

- 结案档：**KV 一致→排除 KV**（两组同向；标杆洁净）。
- 未用槽有限脏写仅附注卫生。

## 6 · 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格 + 实测状态 |
| `evidence/三层计数.json` | 三层明细 |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/samples/` | 样本 |
| `evidence/reports/` | detector 报告 |
| `evidence/kv_compare.json` | 对账摘要 |
| `evidence/kv_v516_numeric_first.json` | v5.16 |
| `evidence/kv_finite_unused.json` | 有限性/未用槽 |
| `evidence/kv_pairs_recap.json` | 成对路径 |

## 7 · 上游 PR 关系

见 [evidence/规格说明.md](./evidence/规格说明.md)（#39283 / #43741）。本 README 不把「构造预期在 KV」写成已证根因。
