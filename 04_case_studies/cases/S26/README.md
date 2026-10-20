# S26 · RMSNorm fp32 weight-mul（PASS · PR-rooted）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
| 三层率 | **354 / 16 / 48**（现行；detect=48/48） |
| Detector | `token_repeat`（**threshold=8**） |
| Origin | `both` |
| Guard pin | G2 f2aefd068 |
| 模型 | Qwen3-8B |
| Run | 与 S25 同技巧 |

## 1 · 现象

`1.1.1…` 复读塌缩；`token_repeat`×48。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 根因

Soft-inverse [vLLM#42379](https://github.com/vllm-project/vllm/pull/42379)：`AscendRMSNorm.forward_oot` 用 fp32-mul 再 cast（错误公式）。属 L2 dtype/cast 类。

## 3 · Guard 结果

**PASS。** 现行 **354 / 16 / 48**。

## 4 · 复现技巧（必读）

与 S25 **同一技巧**——负载形状决定能不能打出目标特征：

| 项 | 正确（照这个做） |
|----|------------------|
| Overlay | `gen_s26_overlay.py` 就地改 B |
| Prompt | `Name one famous river. One short English sentence. id={i}.` |
| 并发 | **48 并发** |
| 其它 | `max_tokens=48`；temp=0 |
| detector | `token_repeat` **threshold=8** |

勿用：中文回声 / 串行 8 / 阈值 16。禁止 force-NaN。脚本：`s26_concurrent_repro.py`、`gen_s26_overlay.py`。

## 5 · 教学要点

对外保留案例里 RMSNorm 的 PR-rooted 代表。复现时先对齐 48 并发河名句 + threshold 8，再谈 PASS/FAIL。

## 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/status.json` | 结案摘要 |
| `evidence/layers.json` | 三层 354/16/48 |
| `evidence/samples/` | 样本 |
| `evidence/reports/` | token_repeat report |
| `evidence/overlay.patch` | overlay |
| `evidence/SPEC_excerpt.md` | SPEC / 上游锚点 |
| `evidence/WHY_PASS.md` | 为何 PASS |

## 上游 PR 关系

| PR / 链接 | 角色 |
|-----------|------|
| [vLLM#42379](https://github.com/vllm-project/vllm/pull/42379) | **根因修复**；本包 soft-inverse |
