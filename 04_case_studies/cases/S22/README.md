# S22 · Spec resample 无 SALT（PASS · spec_acceptance）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
| 三层率 | **126 / 0 / 47**（二次盲跑对齐后现行） |
| Detector | `spec_acceptance`（主）+ `token_repeat` |
| Origin | `ascend-only`（+ vLLM#61161 cousin） |
| Guard pin | G2 f2aefd068（已缺 RESAMPLE_NOISE_SALT） |
| 模型 | Qwen3-8B + eagle3，temp=0.8，num_spec=3 |
| Run | 二次盲跑对齐（首轮曾因 CRLF/LF patch 对不上） |

## 1 · 现象

acceptance_rate 异常偏低。主检出靠 `spec_acceptance`（detect≈47）。

## 2 · 根因

拒绝校验与 residual resample 共用 RNG，没有独立 salt，恢复 token 会偏置（[ascend#18657](https://github.com/vllm-project/vllm-ascend/pull/18657)）。Overlay **只打 trigger 日志**，不造 NaN。与 S05 不同类。

## 3 · Guard 结果

**PASS。** 主 detector 是 **`spec_acceptance`**，不是 `logits_finite`。三层 **126 / 0 / 47**。

## 4 · 复现与环境坑（CRLF vs LF）

**正确做法：** 跑 `gen_s22_overlay.py` / `s22_concurrent_repro.py`——用**锚点字符串替换**，按源文件实际换行（CRLF 或 LF）自适应。

负载：eager / util=0.40；concurrent 48；temp=0.8。

首轮盲跑曾 **PATCH_FAIL**：对静态 patch 做 `git -C B apply` 时，**B 源文件是 CRLF、patch 是 LF** → hunk 对不上。不是缺文件。

**修复（任选）：**

1. 用 `scripts/apply_anomaly_overlay.sh`（会依次尝试 `--ignore-whitespace` / `--ignore-space-change`）；或  
2. 统一换行后再 apply；或  
3. **推荐**：直接跑 `gen_s22_overlay.py` 锚点脚本。

## 5 · 别人按包能核对什么

Spec 路径要用对 detector。acceptance 塌缩时，不要硬套「是否复读」阈值去解释。
