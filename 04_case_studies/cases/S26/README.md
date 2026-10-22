# S26 · RMSNorm fp32 weight-mul（复现未抓到）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **复现未抓到** |
| 检测 | **检出** |
| 三层率 | **354 / 16 / 48**（现行；detect=48/48；trigger/precision 随并发浮动，detect 为判定口径） |
| Detector | `token_repeat`（**threshold=8**） |
| Origin | `both` |
| Guard pin | G2 f2aefd068 |
| 模型 | Qwen3-8B |
| Run | 与 S25 同技巧 |

## 1 · 现象

输出变成反复的数字串（如 `1.1.1…`）；`token_repeat`×48。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 根因

Soft-inverse [vLLM#42379](https://github.com/vllm-project/vllm/pull/42379)：`AscendRMSNorm.forward_oot` 用 fp32-mul 再 cast（错误公式）。属 dtype/cast 问题类（构造已知；定界须另有对账事实）。

## 3 · Guard 结果

**检出。** 现行 **354 / 16 / 48**。结案档：**复现未抓到**。

## 4 · 复现技巧（必读）

与 S25 **同一现行复现**——负载形状决定能不能打出 `1.1.1…`：

| 项 | 现行复现（照这个做） |
|----|----------------------|
| Overlay | `gen_s26_overlay.py` 就地改 B |
| Prompt | `Name one famous river. One short English sentence. id={i}.`（英文河名短句） |
| 并发 | **48 路同时发请求** |
| 其它 | `max_tokens=48`；temp=0 |
| detector | `token_repeat` **threshold=8** |
| 脚本 | `s26_concurrent_repro.py`、`gen_s26_overlay.py` |

**历史错跑（不要照这个结案）：** 曾用「中文回声式」prompt、大约 **8 条串行**请求、阈值 **16** → 往往打不出数字复读、detect=0。这是复现条件不对，不是漏检。

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
| [vLLM#42379](https://github.com/vllm-project/vllm/pull/42379) | **根因修复**；本包 soft-inverse（按上游修复反向注入） |
