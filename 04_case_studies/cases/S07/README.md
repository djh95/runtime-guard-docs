# S07 · W8A8 scale collapse → 无 NaN 乱码（KV 不一致→定界 · 弱窗）

公开自洽案例包。对照：[S01](../S01/)（dense **未复现**，不是漏检）。本包是**真有乱码**，但logits 没有 NaN/Inf，专用 NaN 检测抓不住。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 不一致→定界（弱窗/力度有限）** |
| 检测 | **乱码漏检** |
| 三层率 | **2624 / 1（跨请求内容相同×48） / 0** |
| Detector | 期望 `logits_finite` → **miss**（0 report） |
| Origin | `both` |
| Guard pin | G2 f2aefd068 |
| 模型 | Qwen3-8B-W8A8 TP2 |
| Scenario | `07_quant_scale_collapse` |
| Run | 07_quant_scale_collapse-20261016T084241 |

## 1 · 现象

这里能直接看到**真实的乱码 / 混合脚本垃圾输出**（不是评分把正常中文误判成异常），而且是**跨请求内容相同的乱码**×48（见 [④ 名词表](../../README.md#名词怎么读先看这里)：多次独立请求输出同一段垃圾，不是每次随机不同）。归档样本见 [evidence/samples/](./evidence/samples/)。这和 S01 那篇通顺散文不同。

## 2 · 根因

W8A8 dequant scale 崩溃（在 `deq_scale` 上 zero + 1e20）。属于 quant / scale 族。上游：[vLLM#37442](https://github.com/vllm-project/vllm/pull/37442)。更完整复现字段见 [evidence/规格说明.md](./evidence/规格说明.md)。构造纪律（origin-faithful：禁止强制写 NaN / token fill）见规格与 overlay，**不是**复现负载技巧。

## 3 · Guard 结果

**乱码漏检。** 开了 `logits_finite`（专门抓 logits 里的 NaN/Inf），但本包乱码的 logits 一直是普通有限数字、没有 NaN/Inf，所以 **detect=0**——文字坏了也报不出来。人工看 samples / score 仍是跨请求同一段乱码×48。  
结案档：**KV 不一致→定界（弱窗/力度有限）**——没检出也能拿已有异常 KV dump 去对账；只是这份 dump 很弱（几乎只有 1 个输出 token），定界力度有限。

| 层 | 归档 |
|----|------|
| trigger / precision / detect | **2624 / 1（跨请求内容相同×48） / 0** |

status 里 precision 记成 1，但 samples + score 证实跨请求内容相同的乱码×48——**以 samples + score 为准**。

## 4 · 复现技巧

按本包 pin / 模型 / overlay 对齐三层率即可。Trigger 极高（2624）。

## 5 · 定界分析
### 事实

- **坏输出：** 真乱码，且多次请求吐出**同一段**垃圾；logits **没有** NaN/Inf（所以只盯 NaN 的检测器会漏）。
- **检测：** `logits_finite` 没命中（detect=0）= 乱码漏检。  
  **没检出 ≠ 不能做 KV 对账**：包里另有一份异常侧 KV 快照，用来和干净侧标杆比。这份快照当时几乎只带了 **1 个输出 token**（对比窗主要在 prompt 上）→ 所以叫「弱窗」。
- **对比结果**（`evidence/kv_compare.json`）：相似度阈值 0.99；prompt 约 16 个 token、对齐了 72 层。**两边 KV 对不上。**
- **第一次对不上在哪：** 从 prompt 的**第 0 个 token** 就开始；在第 36 层上，相似度直接算成 NaN（已坏到无法得到正常相似度）。
- **对不上之后：** 没有「后面又变回差不多一样」；因为几乎没有输出 token 入窗，**算不出**「第一个输出 token 像不像」；也**不是**「只有 Prefill/Decode 拆机才出现」这类现象。

### 推断

- KV 对不上 → **还不能排除 KV 这条线**（写坏 / 传坏 / 脏读等仍可能），要继续查。
- 但 dump 太弱（输出几乎只有 1 个 token）→ **定界力度有限**，不能据此写成「就是 W8A8 dequant」。
- 乱码本身也不能直接等于某个具体根因。

### 结论

- 结案档：**KV 不一致→定界（弱窗/力度有限）**；检测侧 **乱码漏检**。
- 尚未定界到 W8A8 dequant / 具体写传路径；分析不出 / 证据不足。

## 6 · 证据文件
| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格（Origin / 锚点 / overlay / knobs / 期望 detector） |
| `evidence/三层计数.json` | 三层明细（trigger / precision / detect） |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/samples/` | prompt + completion 样本 |
| `evidence/kv_compare.json` | 最新 KV 标杆对比摘要（余弦 / 首不一致 / 结论） |

## 7 · 上游 PR 关系
| PR / 链接 | 角色 |
|-----------|------|
| [vLLM#37442](https://github.com/vllm-project/vllm/pull/37442) | **根因修复**（quant / dequant scale 族） |
