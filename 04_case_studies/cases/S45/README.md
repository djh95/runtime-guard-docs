# S45 · Top-k on −logits（KV 一致→排除 KV · 乱码漏检）

公开自洽案例包。detect=0（GAP）→ 用 `manual_dump` 抓异常 KV 再对账。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 一致→排除 KV**（prompt 窗） |
| 检测 | **乱码漏检**（`token_repeat`+`logits_finite` 均 0 report） |
| 三层率 | **16 / 16 / 0**（identical-mode「-Semit修为」×16；另有空 completion） |
| Detector | 期望 `token_repeat`+`logits_finite` → **miss** |
| Origin | 见规格 |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) |
| 模型 | Qwen3-8B · TP2 · CARD=4,5 · temp=0.8 · top_k=1 · `192.168.13.160` / `rg-test-160` |
| Run | `keep-set-retest-20261022` · `S45-layers-20261023T113411` · dump `S45-pr19285-20261023T120202` |

## 1 · 现象

样本见 [evidence/samples/](./evidence/samples/)：乱码 / 空 completion；跨请求可相同（`-Semit修为`×16）或各异。**无** detector report。

## 2 · 案例背景 / 构造

top-k/top-p 打在 −logits（bottom nucleus）。细节见 [evidence/规格说明.md](./evidence/规格说明.md)。**构造背景不是本包 KV 已证根因。**

## 3 · Guard 结果

**乱码漏检。** 开了 `both`，**detect=0**。三层 **16 / 16 / 0**。异常 KV 靠 **`manual_dump`**（incident=`manual_trigger`）当场抓，不是 `on_trigger`。

## 4 · 复现技巧

| 项 | 现行复现 |
|----|----------|
| Overlay | `gen_s45_overlay.py`（双树：Ascend platform + vllm sampler） |
| 请求 | temp=**0.8** · **top_k=1** · concurrency 48 |
| 抓 dump | detect=0 → `manual_dump` 水位递增；合入 #19285 |
| 标杆 | 清洁树；force-feed history |
| 纪律 | 双树 `git checkout -- .`（勿留 S33 等脏写） |

## 5 · 定界分析

### 事实

- **≥2 组**清洁标杆；shape 一致；窗为 **prompt-only**（report `o=1` → `n_cmp=14`）。
- **v5.16（两对同向）：** 数值问题格 **0**；`first_cos_mismatch` **无**（全程 clean；token0 最差仍 ≈1.0）。
- 未用槽：一对异常侧**有限非 0**（卫生）；标杆未用全 0。
- 证据：`evidence/kv_compare.json` + `kv_v516_numeric_first.json`；`verified_kv/S45/ref_recap/`（**.pt 未入库**）。

### 推断

- 有效对账匹配 → **排除「坏值经/进 KV」为主因路径**（就本 prompt 窗、本 head、matched 层而言）。
- 乱码仍现且 detect=0 → 问题更可能在采样/top-k 方向等 **非本包 KV 对比覆盖** 路径；**不能**从 KV 推出 top-k 根因。

### 结论

- 结案档：**KV 一致→排除 KV**（两组同向；标杆洁净；prompt 窗）。
- 检测侧：**乱码漏检**。

## 6 · 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格 + 实测状态 |
| `evidence/三层计数.json` | 三层明细 |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/samples/` | prompt + completion 样本 |
| `evidence/reports/` | `manual_trigger` 报告（非 detector） |
| `evidence/kv_compare.json` | 对账摘要 |
| `evidence/kv_v516_numeric_first.json` | v5.16 数值门闩 + 余弦 |
| `evidence/kv_finite_unused.json` | 有效/未用槽有限性 |
| `evidence/kv_pairs_recap.json` | 成对路径 |

## 7 · 上游 PR 关系

见 [evidence/规格说明.md](./evidence/规格说明.md)。本 README 不重复实测外推断。
