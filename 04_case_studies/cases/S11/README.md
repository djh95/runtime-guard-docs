# S11 · MLA RoPE pad（KV 不一致→定界）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 不一致→定界** |
| 检测 | **检出** |
| 三层率 | **108 / 27 / 48**（`token_repeat`×48） |
| Detector | `token_repeat` |
| Origin | 见规格 |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) |
| 模型 | DeepSeek-V2-Lite（MLA）· TP2 · CARD=4,5 · `192.168.13.160` / `rg-test-160` |
| Run | `keep-set-retest-20261022` · `S11-layers-20261023T125037` |

## 1 · 现象

检出 `token_repeat`（precision=27）。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 案例背景 / 构造

MLA prefill RoPE pad 错位。细节见 [evidence/规格说明.md](./evidence/规格说明.md)。

## 3 · Guard 结果

**检出。** **108 / 27 / 48**。结案档：**KV 不一致→定界**（v5.16：无数值问题；首余弦分歧 @ prompt token1 dump `layer_27`；两组同向；tok0 model 层仍 clean）。

## 4 · 复现技巧

| 项 | 现行复现 |
|----|----------|
| Overlay | `11_mla_rope_pad.patch` |
| 模型 | DeepSeek-V2-Lite |
| 负载 | pad 变长 prompt · churn |
| detector | `token_repeat` |

## 5 · 定界分析

### 事实

- **≥2 组**清洁标杆；shape 一致。
- **v5.16（两对同向）：** 数值问题格 **0**；`first_cos_mismatch` @ **token_idx=1** dump `layer_27`（cos≈0.96）；min_cos≈0.24 @ `model.layers.16.self_attn.attn`。
- token0 model 层最差仍 ≈1.0。
- 未用槽：异常侧有限非 0（卫生）。
- 证据：`evidence/kv_*.json`（**.pt 未入库**）。

### 推断

- 有效槽余弦已分 → **定界到本窗首分歧**（token1 / `layer_27`）；不定界到 RoPE 源码行。

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

见规格（ascend#18798）。
