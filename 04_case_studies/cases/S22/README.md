# S22 · Spec resample 无 SALT（PASS · spec_acceptance）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
| 三层率 | **126 / 0 / 47**（现行） |
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

**PASS。** 主 detector 是 **`spec_acceptance`**，不是 `logits_finite`。三层 **126 / 0 / 47**。

## 4 · 复现技巧与环境坑（CRLF vs LF）

**正确做法：** 跑 `gen_s22_overlay.py` / `s22_concurrent_repro.py`——用**锚点字符串替换**，按源文件实际换行（CRLF 或 LF）自适应。

负载：eager / util=0.40；concurrent 48；temp=0.8。

对静态 patch 做 `git -C B apply` 时，若 **B 源文件是 CRLF、patch 是 LF** → hunk 对不上（PATCH_FAIL）。不是缺文件。

**修复（任选）：**

1. 用 `scripts/apply_anomaly_overlay.sh`（会依次尝试 `--ignore-whitespace` / `--ignore-space-change`）；或  
2. 统一换行后再 apply；或  
3. **推荐**：直接跑 `gen_s22_overlay.py` 锚点脚本。

## 5 · 教学要点

Spec 路径要用对 detector（主看 `spec_acceptance`）。acceptance 塌缩时，不要硬套「是否复读」阈值去解释。

## 定界分析

1. **L1 detect 停点**——detect：主靠 `spec_acceptance`（detect=47）。
2. **L2 class-hint**——L2 class-hint：spec resample RNG/SALT（分布性）；≠S05 NaN。
3. **标杆 / Q1–Q5**——无 buggy+ref 标杆 → Q1–Q5 不适用 / KV=未知。
4. **结合现象**——见 `evidence/samples/` · `evidence/reports/`。
5. **结案要点**——PASS；CRLF 源需锚点脚本 / ignore-whitespace。

## 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格（Origin / 锚点 / overlay / knobs / 期望 detector） |
| `evidence/三层计数.json` | 三层明细（trigger / precision / detect） |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/samples/` | prompt + completion 样本 |
| `evidence/reports/` | Guard detector 报告 |


## 上游 PR 关系

| PR / 链接 | 角色 |
|-----------|------|
| [ascend#18657](https://github.com/vllm-project/vllm-ascend/pull/18657) | **根因修复**（resample salt） |
| [vLLM#61161](https://github.com/vllm-project/vllm/pull/61161) | **对照 cousin**（非本 pin 主修复） |
