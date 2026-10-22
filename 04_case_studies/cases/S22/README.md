# S22 · Spec resample 无 SALT（复现未抓到）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **复现未抓到** |
| 检测 | **检出** |
| 三层率 | **126 / 0 / 47**（现行；trigger/precision 随并发浮动，detect 为判定口径） |
| Detector | `spec_acceptance`（主）+ `token_repeat` |
| Origin | `ascend-only`（+ vLLM#61161 cousin） |
| Guard pin | G2 f2aefd068（已缺 RESAMPLE_NOISE_SALT） |
| 模型 | Qwen3-8B + eagle3，temp=0.8，num_spec=3 |
| Run | 锚点 overlay + concurrent 48 |

## 1 · 现象

acceptance_rate 异常偏低。主检出靠 `spec_acceptance`（detect≈47）。

## 2 · 根因

拒绝校验与 residual resample 共用 RNG，没有独立 salt，恢复 token 会偏置（[ascend#18657](https://github.com/vllm-project/vllm-ascend/pull/18657)）。Overlay **只打 trigger 日志**，不造 NaN。与 S05 不同类。

## 3 · Guard 结果

**检出。** 主 detector 是 **`spec_acceptance`**，不是 `logits_finite`。三层 **126 / 0 / 47**。结案档：**复现未抓到**。

## 4 · 复现技巧（CRLF vs LF）

**正确做法：** 跑 `gen_s22_overlay.py` / `s22_concurrent_repro.py`——用**锚点字符串替换**，按源文件实际换行（CRLF 或 LF）自适应。

负载：eager / util=0.40；concurrent 48；temp=0.8。

对静态 patch 做 `git -C B apply` 时，若 **B 源文件是 CRLF、patch 是 LF** → hunk 对不上（PATCH_FAIL）。不是缺文件。

**修复（任选）：**

1. 用 `scripts/apply_anomaly_overlay.sh`（会依次尝试 `--ignore-whitespace` / `--ignore-space-change`）；或 
2. 统一换行后再 apply；或 
3. **推荐**：直接跑 `gen_s22_overlay.py` 锚点脚本。

## 5 · 定界分析

### 事实

- 现象 / 检测见上文钉点与 samples（或 reports）。
- **有效 KV 对账：无。** 本包曾归档的 `kv_compare.json` 及其中「首不一致 / 层号 / 余弦」结论**全部撤回**（新旧跑次混用、空 prompt、弱窗、全 NaN 占位等问题，不可信）。

### 推断

- 在重做**同一次异常请求**的有效异常 dump ↔ 标杆对账之前，**不能**得出「排除 KV」或「KV 不一致定界」。
- 坏输出 / 构造预期 ≠ 已证根因。

### 结论

- 结案档：**复现未抓到**（有异常或检出证据，但无有效异常 KV 可对账）。
- **尚未做有效 KV 对账**；分析不出 / 证据不足。


## 6 · 证据文件
| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格（Origin / 锚点 / overlay / knobs / 期望 detector） |
| `evidence/三层计数.json` | 三层明细（trigger / precision / detect） |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/samples/` | prompt + completion 样本 |
| `evidence/reports/` | Guard detector 报告 |

## 7 · 上游 PR 关系
| PR / 链接 | 角色 |
|-----------|------|
| [ascend#18657](https://github.com/vllm-project/vllm-ascend/pull/18657) | **根因修复**（resample salt） |
| [vLLM#61161](https://github.com/vllm-project/vllm/pull/61161) | **对照 cousin**（非本 pin 主修复） |
