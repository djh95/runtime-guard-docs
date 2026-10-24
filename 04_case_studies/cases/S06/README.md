# S06 · MoE 路由 bias（KV 不一致→定界）

公开案例包。专家路由被弄偏后出现 token 复读；检测抓住了；KV 对账两边对不上 → **KV 不一致→定界**（坏值已进/经 KV，但不能单凭对账写死「根因=路由某行」）。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 不一致→定界** |
| 检测 | **检出** |
| 三层率 | **52 / 25 / 46**（触发 / 判坏 / 报告；`token_repeat`×46；共 48 请求） |
| Detector | `token_repeat` |
| Origin | 见规格 |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) |
| 模型 | DeepSeek-V2-Lite · TP2 · CARD=4,5 · `192.168.13.160` / `rg-test-160` |
| Run | `keep-set-retest-20261022` · `S06-layers-20261023T122714` |

## 1 · 现象

约 25/48 被判成坏输出；重复-token 检测命中。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 案例背景 / 构造

MoE（混合专家）路由 bias / 掩码按故障模式注入。细节见 [evidence/规格说明.md](./evidence/规格说明.md)。**构造故事≠本包 KV 已证根因。**

## 3 · Guard 结果

**检出。** **52 / 25 / 46**。结案：**KV 不一致→定界**——无数值崩溃；从 prompt 第 1 个 token 起与干净对照的相似度就分叉（见事实）。

## 4 · 复现技巧

| 项 | 怎么做 |
|----|--------|
| Overlay | 见规格 / 生成脚本 |
| 模型 | DeepSeek-V2-Lite |
| detector | `token_repeat` |
| 抓对照 KV | 干净服务上按报告里的 **token id 原样重放**（不要把字符串再分词一遍） |

## 5 · 定界分析

### 事实

- **清洁标杆（≥2 组）：** 干净服务重放对照；**2 组**；shape 一致（本模型 MLA 窗为 `[1,128,1,64]`）。对比窗含 prompt+生成（约 `n_prompt=14`，`p+o−1`≈21）。
- **两对同向：** 两对都无数值问题，且都在 prompt 第 1 个 token 上出现余弦分歧。
- **数值门闩：** 无 NaN/Inf/全零类问题 → 继续看余弦（看异常 KV 与标杆有多像；阈值约 0.99）。
- **余弦：** prompt 第 1 个 token 起，dump 全名排序下首次明显偏离在 `layer_27`（余弦≈0.05）；只看 `model.layers.*` 时，首次越阈约在 **`model.layers.4`**（余弦≈0.85）。最差可到负相关量级（见 evidence）。
- **dump 双名（本窗）：** 合计约 54 个张量名 = 27 个 `model.layers.0…26…` + 27 个 `layer_27…53`。对应关系是 `layer_(27+i)` ↔ `model.layers.i`，所以 **`layer_27` = 模型第 0 层的另一套文件名**，不是「第 27 层」。脚本先扫到 `layer_27`，模型路径叙事则写第 4 层首越阈——同一套对账、两套名字。
- 证据：`evidence/kv_compare.json`、`kv_v516_numeric_first.json`（**.pt 未入库**）。

### 推断

- 有效槽相似度已分 → **KV 线要重开**；层号是对账定位，不是「根因=第 N 层」。
- 不定界到具体 router 源码行。

### 结论

- 结案档：**KV 不一致→定界**（两组同向）。

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
