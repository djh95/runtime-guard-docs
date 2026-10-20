# S25 · RoPE second-half drop（PASS · PR-rooted）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
| 三层率 | **348 / 17 / 48**（现行；detect=48/48） |
| Detector | `token_repeat`（**threshold=8**） |
| Origin | `ascend-only` |
| Guard pin | G2 f2aefd068 |
| 模型 | Qwen3-8B |
| Run | 河名句 + 48 并发 + 阈值 8 |

## 1 · 现象

输出塌成 `1.1.1…` / `1.0.0…` 复读；`token_repeat`×48。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 根因

Soft-inverse [ascend#7082](https://github.com/vllm-project/vllm-ascend/pull/7082)：`npu_rotary_embedding` 后恢复未旋转的后半维（缺 store 语义）。不等于 S11 的 pad 长度问题。

## 3 · Guard 结果

**PASS。** 现行 **348 / 17 / 48**。

## 4 · 复现技巧（必读）

`1.1.1…` 塌缩**只在**下列技巧下稳定出现：

| 项 | 正确（照这个做） |
|----|------------------|
| Overlay | `gen_s25_overlay.py` 就地改 B 树 |
| Prompt | `Name one famous river. One short English sentence. id={i}.` |
| 并发 | **48 并发**（勿串行 8 条） |
| 其它 | `max_tokens=48`；temp=0 |
| detector | `token_repeat` **threshold=8**（勿用 16） |

勿用：中文回声 / 串行 8 / 阈值 16（会无塌缩、detect=0，属错跑法，不是漏检）。

脚本：`s25_concurrent_repro.py`、`gen_s25_overlay.py`。

## 5 · 教学要点

写 RoPE 案例要写清「不等于 S11」。负载技巧错了，结论也会错——无塌缩时 detect=0 不要写成漏检。

## 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/status.json` | 结案摘要 |
| `evidence/layers.json` | 三层 348/17/48 |
| `evidence/samples/` | 样本 |
| `evidence/reports/` | token_repeat report |
| `evidence/overlay.patch` | overlay |
| `evidence/SPEC_excerpt.md` | SPEC / 上游锚点 |
| `evidence/WHY_PASS.md` | 为何 PASS |

## 上游 PR 关系

| PR / 链接 | 角色 |
|-----------|------|
| [ascend#7082](https://github.com/vllm-project/vllm-ascend/pull/7082) | **根因修复**；本包 soft-inverse |
