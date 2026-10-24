# S23 · 一层 o_proj 权重置零（KV 不一致→定界）

公开案例包。加载后把某一层输出投影权重清零；部分请求变成数字复读；检测全抓住；KV 对账与干净对照对不上。**构造在权重，不是「已证 KV 子系统根因」。**

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 不一致→定界** |
| 检测 | **检出** |
| 三层率 | **2 / 16 / 48**（触发很少 / 判坏 16 / 报告 48） |
| Detector | `token_repeat`（重复阈值=8） |
| Origin | `both`（构造型权重故障） |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) |
| 模型 | Qwen3-8B · TP2 · CARD=4,5 · `192.168.13.160` / `rg-test-160` |
| Run | 英文河名短句 ×48；`keep-set-retest-20261022` |

## 1 · 现象

部分请求塌成 `1.1.1…` / `0.1.0…`（约 16/48）；重复检测 48/48 命中。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 案例背景 / 构造

启动后置零一层 `o_proj.weight`。细节见 [evidence/规格说明.md](./evidence/规格说明.md)。

## 3 · Guard 结果

**检出。** **2 / 16 / 48**（注入几乎不打触发日志，但复读仍被抓住）。结案：**KV 不一致→定界**。

## 4 · 复现技巧

| 项 | 怎么做 |
|----|--------|
| Overlay | `gen_s23_overlay.py` |
| Prompt | `Name one famous river… id={i}.` ×48 |
| detector | `token_repeat`，阈值 8 |
| 配置 | 服务 READY 后须**重写** runtime 配置（防止 worker 把检测又关掉） |
| 抓 dump | #19285；清 kv cache |

## 5 · 定界分析

### 事实

- **清洁标杆（≥2 组）：** 干净服务重放对照；**2 组**；shape 一致。history 按 `p+o−1`（两组长度约 21 / 20）。标杆侧未亮 `logits_finite`。
- **有效槽：** 有限（无 Inf/NaN）。**未用槽**有限非 0 → **卫生**（通常不致坏结果）。
- **余弦（两对同向）：** 最低约 0.68；首个不一致都在 **prompt 第 2 个 token**、`model.layers.35`（脚本层定位）。权重注入可以解释为「算子写出污染了 KV」，**不要**升格成「根因=第 35 层」以外的断言。
- **三层旁注：** trigger 很低（2）仍 detect=48——注入几乎不打日志，但输出复读仍被抓住。
- 证据：`evidence/kv_compare.json`、`kv_finite_unused.json`（**.pt 未入库**）。

### 推断

- 对账不匹配 → **重开 KV 线**（坏值已进/经 KV）。
- 与「权重写出污染」相容，**不能**从本包推出具体 weight 名已证。

### 结论

- 结案档：**KV 不一致→定界**。
- 尚未定界到构造根因算子/提交。

## 6 · 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 补丁 |
| `evidence/规格说明.md` | 规格 |
| `evidence/三层计数.json` / `跑批结果.json` | 三层 / 摘要 |
| `evidence/samples/` / `reports/` | 样本 / 报告 |
| `evidence/kv_*.json` | 对账 / 有限性 |

## 7 · 上游 PR 关系

构造型权重故障；无单独「修复本 overlay」上游 PR。#19285 仅抓 dump 辅助。
