# S22 · Spec resample 无 SALT（PASS · spec_acceptance）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
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

### 事实

- 三层：126 / 0 / 47；主 detector：`spec_acceptance`（detect=47；`evidence/reports/`）。
- sample / report：acceptance 塌缩相关现象（`evidence/samples/`）；`token_repeat` 条 prompt 为空、`spec_acceptance` 条有。
- 包内无标杆 vs 异常 KV 对账结果。

### 推断

- 可确认：`spec_acceptance` 已检出 → PASS 有据。
- 坏输出 / acceptance 塌缩推不出「spec resample RNG/SALT」细因（§2 非定界已证）。
- 无 KV 对账 → 不能排除或确认 KV。

### 结论

- 已定界到：`spec_acceptance` 检出。
- **尚未定界到** resample salt；**分析不出 / 证据不足**。
- KV：路径可用；归档尚未附结论。
- **定界结论：L1** = `spec_acceptance` 已命中；**L2** = 证据不足。
- 结案：PASS。


## 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格（Origin / 锚点 / overlay / knobs / 期望 detector） |
| `evidence/三层计数.json` | 三层明细（trigger / precision / detect） |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/samples/` | prompt + completion 样本 |
| `evidence/reports/` | Guard detector 报告（`token_repeat` 条 prompt 为空、`spec_acceptance` 条有；空因见 [④ 名词表](../../README.md#名词怎么读先看这里)，可读 prompt 亦可看 samples） |


## 上游 PR 关系

| PR / 链接 | 角色 |
|-----------|------|
| [ascend#18657](https://github.com/vllm-project/vllm-ascend/pull/18657) | **根因修复**（resample salt） |
| [vLLM#61161](https://github.com/vllm-project/vllm/pull/61161) | **对照 cousin**（非本 pin 主修复） |
