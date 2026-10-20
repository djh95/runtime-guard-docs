# S26 · RMSNorm fp32 weight-mul（PASS · PR-rooted）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
| 三层率 | **354 / 16 / 48**（二次盲跑对齐后现行；detect=48 精确） |
| Detector | `token_repeat`（**threshold=8**） |
| Origin | `both` |
| Guard pin | G2 f2aefd068 |
| 模型 | Qwen3-8B |
| Run | 二次盲跑对齐（与 S25 同配方） |

## 1 · 现象

`1.1.1…` 复读塌缩；`token_repeat`×48。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 根因

Soft-inverse [vLLM#42379](https://github.com/vllm-project/vllm/pull/42379)：`AscendRMSNorm.forward_oot` 用 fp32-mul 再 cast（错误公式）。属 L2 dtype/cast 类。

## 3 · Guard 结果

**PASS。** 现行 **354 / 16 / 48**。

## 4 · 复现配方（必读）

与 S25 **同一配方**——负载形状决定能不能打出目标特征：

| 项 | 正确（照这个做） |
|----|------------------|
| Overlay | `gen_s26_overlay.py` 就地改 B |
| Prompt | `Name one famous river. One short English sentence. id={i}.` |
| 并发 | **48 并发** |
| 其它 | `max_tokens=48`；temp=0 |
| detector | `token_repeat` **threshold=8** |

首轮盲跑「FAIL detect=0」同属**错配方**（中文回声 + 串行 8 + 阈值 16），不是检测器漏检。二次盲跑对齐后 → **354 / 16 / 48** PASS（detect=48 精确）。

禁止 force-NaN。脚本：`s26_concurrent_repro.py`、`gen_s26_overlay.py`。

## 5 · 别人按包能核对什么

对外保留案例里 RMSNorm 的 PR-rooted 代表。复现时先对齐 48 并发河名句 + threshold 8，再谈 PASS/FAIL。
