# S45 · Top-k 打在 −logits 上（KV 一致→排除 KV · 乱码漏检）

公开案例包。采样时 top-k 作用在**取反后的 logits** 上（等于专挑最差的候选）。**乱码会出现，但检测 0 份报告**——**乱码漏检**。异常 KV 靠**手动 dump** 再对账；本窗对账干净 → **排除 KV 主因**（且生成很短，主要只对上了 prompt 段）。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 一致→排除 KV**（本次主要只对上了 prompt 段的 KV） |
| 检测 | **乱码漏检**（`token_repeat` 与 `logits_finite` 都是 0 份报告） |
| 三层率 | **16 / 16 / 0**（触发 / 判坏 / 报告；约 16 条相同乱码串「-Semit修为」，另有空输出） |
| Detector | 期望两者都开 → **都没响** |
| Origin | 见规格 |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) |
| 模型 | Qwen3-8B · 温度 0.8 · top_k=1 · TP2 · CARD=4,5 |
| Run | `keep-set-retest-20261022` · `S45-layers-20261023T113411` · dump `S45-pr19285-20261023T120202` |

## 1 · 现象

乱码或空 completion；有的跨请求相同，有的各异。样本见 [evidence/samples/](./evidence/samples/)。**没有**检测报告。

## 2 · 案例背景 / 构造

top-k / top-p 打在 −logits（bottom nucleus）。细节见 [evidence/规格说明.md](./evidence/规格说明.md)。**构造背景不是本包 KV 已证根因。** 须同时改 Ascend 与上游 vLLM 采样文件（双树）。

## 3 · Guard 结果

**乱码漏检。** 开了两种检测，**报告数仍为 0**。三层 **16 / 16 / 0**。异常 KV 靠手动 dump 当场抓，不是「检测触发后自动 dump」。

## 4 · 复现技巧

| 项 | 怎么做 |
|----|--------|
| Overlay | `gen_s45_overlay.py`（Ascend `platform.py` + vLLM `sampler.py`） |
| 请求 | 温度 **0.8** · **top_k=1** · 并发 48（勿用温度 0） |
| 抓 dump | 检测为 0 → 手动 dump 水位递增；合入 #19285 |
| 对照 | 干净树；按 token id 原样重放 |
| 纪律 | 跑前双树 `git checkout -- .`（勿留别案脏写） |

## 5 · 定界分析

### 事实

- **清洁标杆（≥2 组）：** 干净服务重放对照；**2 组**；shape 一致。抓 dump 时生成很短：报告 **输出只有 1 个 token**，可比长度主要是 prompt（本窗 14）。检测侧 **0 report**（乱码漏检），KV 靠 `manual_dump` 当场抓，不是 on_trigger。
- **两对同向：** 数值问题格 **0**；余弦全程干净（prompt 第 1 个 token 最差仍≈1.0）。
- **未用槽：** 一对异常侧有限非 0（**卫生**）；标杆未用多为 0。
- **读法：** 对账匹配 → **排除「坏值经/进 KV」为主因**（就本 prompt 窗而言）；乱码仍在，更可能落在采样/top-k 方向等本窗 KV 没覆盖到的路径。
- 证据：`evidence/kv_*.json`；`verified_kv/S45/`（**.pt 未入库**）。



### KV 对账表

分桶（可读性）：`≈1`≥0.99；`0.9–0.99`；`0.8–0.9`；`0.6–0.8`；`0.3–0.6`；`0.1–0.3`；`<0.1`（含负值）；数值门闩写清子类型（如 `数值问题:全零(zero_norm)` / `数值问题:NaN` / `数值问题:Inf`），勿只写「数值异常」（不编余弦）。

数据来自 `evidence/kv_v516_numeric_first.json`（及同结构字段）；不编造未入库 `.pt` 上的数。

两对同向时只展示**代表对**（对 1）。

**代表对**（`req_id`=`cmpl-a8b62fdc53007004-0-84d80d11`；对比窗 **14** token，其中 prompt **14**）。

**表1 · 每 token 最差格**（该 token 上差距最大的层；有数值门闩则整格写清子类型）

| token 序号 | 角色 | 该 token 最差格 |
| --- | --- | --- |
| 0 | prompt[0] | ≈1（最差 layer_58） |
| 1 | prompt[1] | ≈1（最差 layer_47） |
| 2 | prompt[2] | ≈1（最差 L12） |
| 3 | prompt[3] | ≈1（最差 layer_36） |
| 4 | prompt[4] | ≈1（最差 layer_39） |
| 5 | prompt[5] | ≈1（最差 layer_36） |
| 6 | prompt[6] | ≈1（最差 layer_42） |
| 7 | prompt[7] | ≈1（最差 layer_41） |
| 8 | prompt[8] | ≈1（最差 layer_39） |
| 9 | prompt[9] | ≈1（最差 layer_55） |
| 10 | prompt[10] | ≈1（最差 layer_37） |
| 11 | prompt[11] | ≈1（最差 layer_43） |
| 12 | prompt[12] | ≈1（最差 layer_42） |
| 13 | prompt[13] | ≈1（最差 layer_36） |

**表2 · 首个出问题的 token 的逐层剖面** — **无问题 token，跳过**（本短窗 prompt 对账全程 ≈1 → 排除 KV；不假装「首坏」）。

一行说明：代表对窗内全程 ≈1（弱窗：主要对上 prompt）。

### 推断

- 对账匹配 → **排除「坏值经/进 KV」为主因**（本 prompt 短窗）。
- 乱码仍在且检测为 0 → 更可能在采样 / top-k 方向等 **本窗 KV 没覆盖** 的路径。

### 结论

- 结案档：**KV 一致→排除 KV**（两组同向；prompt 短窗）。
- 检测侧：**乱码漏检**。

## 6 · 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 补丁 |
| `evidence/规格说明.md` | 规格 + 实测 |
| `evidence/三层计数.json` / `跑批结果.json` | 三层 / 摘要 |
| `evidence/samples/` | 样本 |
| `evidence/reports/` | 手动触发报告（非检测器） |
| `evidence/kv_*.json` | 对账 |

## 7 · 上游 PR 关系

见规格。
