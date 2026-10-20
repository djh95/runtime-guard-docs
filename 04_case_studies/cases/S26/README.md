# S26 · RMSNorm fp32 weight-mul（PASS · PR-rooted）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **PASS**（以 160 concurrent 标杆为准） |
| 三层率 | **470 / 14 / 48** |
| Detector | `token_repeat` |
| Origin | `both` |
| Guard pin | G2 f2aefd068 |
| 模型 | Qwen3-8B |
| Run | 26_rmsnorm_fp32_mul-20261017T115830 @ 160 cards 6,7 |

## 1 · 现象

`1.1.1…` 复读塌缩；`token_repeat`×48。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 根因

Soft-inverse [vLLM#42379](https://github.com/vllm-project/vllm/pull/42379)：`AscendRMSNorm.forward_oot` 用 fp32-mul 再 cast（错误公式）。属 L2 dtype/cast 类。

## 3 · Guard 结果

**PASS。** 归档 **470 / 14 / 48**。

## 4 · 复现：160 成功配方 vs 162 失败配方

与 S25 同一类坑——**负载形状决定能不能打出目标特征**。

| | **160 成功** | **162 曾失败** |
|--|--------------|----------------|
| Overlay | `gen_s26_overlay.py` 就地改 B | 静态 patch `git apply` 到 B |
| 负载 | **48 并发**河名句英文短 prompt；`max_tokens=48`；temp=0 | **8 条**中文回声串行 |
| 特征 | `1.1.1…` 数字塌缩 + detect | 无数字塌缩；detect=0 |

禁止 force-NaN。脚本：`s26_concurrent_repro.py`、`gen_s26_overlay.py`。

## 5 · 学完能做什么

对外保留案例 里 RMSNorm 的 PR-rooted 代表。复现时先对齐 160 的 48 并发河名句，再谈 PASS/FAIL。
