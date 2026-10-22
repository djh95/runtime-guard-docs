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
结案档：**KV 不一致→定界（弱窗/力度有限）**。乱码靠 samples；KV 对账用的是旧短 dump（见 §5），力度有限。

| 层 | 归档 |
|----|------|
| trigger / precision / detect | **2624 / 1（跨请求内容相同×48） / 0** |

status 里 precision 记成 1，但 samples + score 证实跨请求内容相同的乱码×48——**以 samples + score 为准**。

## 4 · 复现技巧

按本包 pin / 模型 / overlay 对齐三层率即可。Trigger 极高（2624）。

## 5 · 定界分析
### 事实

- **坏输出怎么知道的：** 靠 `evidence/samples/`——多次请求同一段乱码（长 completion）。**不是**靠下面这份 KV dump 的 output。
- **检测：** `logits_finite` **detect=0**（乱码漏检）。logits 没有 NaN/Inf，检测器本来就不会因为「乱码文字」开火。
- **KV dump 从哪来：** 旧跑次里有一份挂在 `logits_finite` 路径下的 dump；report 里 **output 几乎只有 1 个 token**。对比窗因此几乎全是 prompt（`n_prompt=n_tokens=16`）。这叫「弱窗」——**不是**「请求发少了」，是**快照拍太早/太短**。
- **对比结果**（`evidence/kv_compare.json`）：阈值 0.99。异常侧 vs 标杆：**对不上**。但每个对比位置的最小余弦都是 **NaN**，脚本把「最差」记成从 `layer_36` 起、token idx=0——这是 **NaN 排序占位**，**不能**读成「精确定位：第 0 个 prompt token × 第 36 层」。S48/S50 也出现同类「全 NaN @ layer_36」写法，更像 dump/对齐算不出有效余弦，而不是三个无关 bug 碰巧同一点坏。
- **第一个输出 token 像不像：** 本窗没有 output 槽，**算不出**。也**没有**用 output 做检测来证明这份 dump 对应乱码请求。

### 推断

- 只能弱说：当前这份对账 **不像 KV 一致**；要坐实「何时污染 / 哪一层」→ 应 **manual_dump 重抓**带足够长 output 的异常请求（对照 S45 做法），不要继续解读这份全 NaN 摘要。
- 不能据此写成 W8A8 dequant 根因；乱码文字本身也不等于具体根因。

### 结论

- 结案档仍记：**KV 不一致→定界（弱窗/力度有限）**；检测侧 **乱码漏检**。
- **时效说明：** 现有 `kv_compare.json` **不够格**做「首分歧位置」叙事；分析不出 / 证据不足，除非重抓。

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
