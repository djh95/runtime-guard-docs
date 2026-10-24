# S43 · Embed ×100（KV 不一致→定界）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 不一致→定界** |
| 检测 | **检出** |
| 三层率 | **16 / 40 / 48**（`token_repeat`×48） |
| Detector | `token_repeat` |
| Origin | 见规格 |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) |
| 模型 | Qwen3-8B · TP2 · CARD=4,5 · `192.168.13.160` / `rg-test-160` |
| Run | `keep-set-retest-20261022` · `S43-layers-20261023T104944` / `S43-pr19285-20261023T105118` / `S43-ref-recap-20261023T105259` |

## 1 · 现象

大量换行塌缩（identical-mode ×40）。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 案例背景 / 构造

embedding ×100。细节见 [evidence/规格说明.md](./evidence/规格说明.md)；补丁见 [evidence/overlay.patch](./evidence/overlay.patch)。**构造根因不是本包 KV 定界已证。**

## 3 · Guard 结果

**检出。** 现行 **16 / 40 / 48**（`detect_by.token_repeat=48`）。结案档：**KV 不一致→定界**（v5.16：无数值问题格；余弦自 token0 不一致）。

## 4 · 复现技巧（必读）

| 项 | 现行复现 |
|----|----------|
| Overlay | `gen_s43_overlay.py` |
| 并发 | **48** |
| detector | `token_repeat` |
| 抓 dump | 临时 #19285；抓前清 `kv_cache` |
| 标杆 | 清洁树无 overlay；manual_dump + force-feed history |

## 5 · 定界分析

### 事实

- **清洁标杆（≥2 组）：** 干净服务重放对照；shape 一致；标杆未用槽归零。history **`p + o − 1 = 18`**（约 prompt=14、生成较短）。
- **两对同向：** 无数值问题；余弦可算，且两对同一套层叙事。
- **余弦：** prompt 第 1 个 token 起，`model.layers.0–1` 仍≈1；自 **`model.layers.2`** 首次明显偏离（余弦≈0.55）；同 token 最差约 −0.30 落在 `model.layers.20`。
- **dump 双名：** 另有 `layer_36…` 一套名字；`layer_36` = `model.layers.0`（`layer_(36+i)` ↔ `model.layers.i`）。全名排序的「首次余弦」可能先写到 `layer_36`，与「模型第 2 层首越阈」是同一对账的不同命名视图。
- **未用槽：** 异常侧有限非 0（**卫生**）。
- 证据：`evidence/kv_*.json`；`verified_kv/S43/`（**.pt 未入库**）。

### 推断

- 有效槽有限但余弦自 prompt token0 / L2 起不一致 → **KV 不一致**类信号。
- 未用槽有限脏写单独不构成「结果由此坏」。
- **不能**单凭 KV 推出「根因=embed ×100」。

### 结论

- 结案档：**KV 不一致→定界**（两组同向；含 first_cos 层事实）。
- 尚未证到构造根因算子名。

## 6 · 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 静态补丁 |
| `evidence/规格说明.md` | 复现规格 |
| `evidence/三层计数.json` | 三层明细 |
| `evidence/跑批结果.json` | 跑批 + 结案摘要 |
| `evidence/samples/` | 样本 |
| `evidence/reports/` | 钉点 report |
| `evidence/kv_compare.json` | v5.16 摘要 |
| `evidence/kv_v516_numeric_first.json` | 逐对明细 |
| `evidence/kv_finite_unused.json` | 有限性/未用槽 |
| `evidence/kv_pairs_recap.json` | 配对元数据 |

## 7 · 上游 PR 关系

| PR / 链接 | 角色 |
|-----------|------|
| （构造；见规格） | 背景，非本包 KV 已证根因 |
| [ascend#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) | 抓 dump 辅助 |
