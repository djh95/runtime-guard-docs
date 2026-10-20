# S01 · KV skip-zero → FAIL（复现未出现）

这是一份公开、自洽的案例包：只靠本目录材料就能读完。

同族里**能检出来**的对照包：[S10′（S10p）](../S10p/)（recycle-zero → `token_repeat` PASS）。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案结论 | **FAIL（复现未出现）** / repro-blocked |
| 三层率（2026-10-20 160 复判） | **154 / 0 / 0**（trigger / precision〔CJK 排除后〕/ detect） |
| 期望 detector | 乱码类；本轮**无可检坏输出**，故不构成 FAIL+GAP |
| Guard pin | G2 · `f2aefd068c4bd299d91cf0a1fdf642a3f327308f` |
| 模型 | Qwen3-8B · TP2 · 稠密 float16 |
| 上游锚点 | [vLLM#43990](https://github.com/vllm-project/vllm/pull/43990) · [#47574](https://github.com/vllm-project/vllm/pull/47574)（角色见文末表） |
| Origin | `both` |
| 三层 / 跑批 | [evidence/三层计数.json](./evidence/三层计数.json) · [evidence/跑批结果.json](./evidence/跑批结果.json) |

## 1 · 现象

Overlay 打上后服务仍 200。可见 completion 是通顺中英散文（华为 NPU / vLLM 介绍），**不是**乱码。样本见 [evidence/samples/](./evidence/samples/)。

**CJK 是什么：** 中日韩字符。评分须排除 CJK 后再计 weird——通顺中文 ≠ `garbage_mixed_script`。本包排除后 weird≈0 → **precision=0**。没有坏输出时，**不要**写成 FAIL+GAP。

### 为何 S01 复现不出、S10′ 可以

| | **S01**（本包） | **S10′** |
|--|-----------------|----------|
| 机制 | 进了 zeroer 再 **skip 置零**（新块脏读） | FullAttn **从不进** zeroing（回收块脏尾） |
| 形态前提 | **hybrid / 量化 KV**；稠密 bf16 上目标乱码不出现 | dense FullAttn + 回收压力即可 |
| 本 pin 实测 | trigger=154，**precision=0**，detect=0 | **65 / 20 / 79**，`token_repeat` PASS |
| 结案 | FAIL（复现未出现） | PASS |

跨请求内容相同的真实乱码见 **S07**（FAIL+GAP；与本包结案不同）。

## 2 · 根因

| 字段 | 值 |
|------|-----|
| Origin | `both`（vLLM 与 Ascend 同失败模式） |
| 语义 | 新分配 KV block **未置零** → 读脏页 |
| 形态前提 | **hybrid / 量化 KV**（不是任意稠密 bf16） |

上游：[#43990](https://github.com/vllm-project/vllm/pull/43990)、[#47574](https://github.com/vllm-project/vllm/pull/47574)；Ascend 对照 `_zero_block_ids` / `AscendKVBlockZeroer`。

完整 overlay（约 251 行 / 5 文件）会：强制 `needs_kv_cache_zeroing`；skip `zero_block_ids`；并在 dense 路径做 **synth_block0**。synth_block0 抬高的是 **trigger 日志**，不等于已经读到脏 KV 乱码。

## 3 · Guard 结果

**判定：FAIL（复现未出现）。** 有 trigger、无真实坏输出、detect=0——缺的是「异常已出现」前提，故不是 GAP 结案。

| 层 | 复判（160 · `T101951`） | 含义 |
|----|------------------------:|------|
| trigger | **154** | skip_zero / synth_block0 / force_should_init（路径打中） |
| precision | **0** | CJK 排除后；通顺中文不算坏输出 |
| detect | **0** | 无 `report_*.json` |

对照：**S10′** = 有坏输出 + detect；**S01 dense** = 只有 trigger。证据清单见文末「证据文件」表。

## 4 · 复现技巧：形态前提

| 维 | 要求 / 实测 |
|----|-------------|
| Origin 形态 | SPEC：**hybrid / 量化 KV** |
| 160 dense（本复判，满量 overlay） | Qwen3-8B float16 · cards `4,5` · `PRODUCT_TREE=B` → trigger=**154**，**0 坏输出** |
| hybrid/fp8 一次尝试 | `--kv-cache-dtype fp8` → Ascend `FP8_ATTENTION` 能力 assert，**起服失败**；不夸大、不另造放大器 |

说明：162 上若仍用残缺 canonical 入口（≈28 行/1 文件），trigger 可恒 0——那是入口未切满量，与本包满量复判（trigger=154、仍无坏输出）不是同一回事。

若要真复现 origin：在**支持量化/hybrid KV**的栈上跑，并归档带 **prompt + completion** 的原始坏样本。dense + synth 只适合验证 trigger 路径。

## 5 · 现行结案摘要

| 项 | 现行 |
|----|------|
| 结案 | **FAIL（复现未出现）** / repro-blocked；**不是** FAIL+GAP |
| 三层 | **154 / 0 / 0**（CJK 排除后 precision=0） |
| 形态 | hybrid/量化 KV 是前提；本 pin 上 fp8 KV 起服失败 |

结案要点已写入下方「定界分析」。

## 6 · 教学要点

1. 分开「有 trigger」和「有坏输出」：本包 dense 复判只有前者 → 记 FAIL（复现未出现），不写 FAIL+GAP。
2. 用排除 CJK 的评分看样本：通顺中文 ≠ `garbage_mixed_script`。
3. 对照 S10′（同 KV 脏读族、能检）与 S07（有乱码+漏检）；本包不是漏检结案。

## 定界分析

（**L1** = 检测停点 / **L2** = 问题类停点；**不是** Transformer 层号。见 [④ 名词表 · L1/L2](../../README.md#名词怎么读先看这里)。）

1. **现象与证据**——detector：本轮 detect=0（无可检坏输出；非漏检结案）。`evidence/samples/` 为通顺中文，不是乱码。dense 栈未见目标坏输出。
2. **排除（已做 / 应做）**——CJK 排除后 precision=0（通顺中文 ≠ 乱码）。形态上提示需 hybrid/量化 KV，稠密 bf16 前提不满足。若日后出现可检报告，仍可走重放抓 ids + KV 对账（见 [④ 名词表 · KV 排除定界](../../README.md#名词怎么读先看这里)）；**本案归档无命中 report，尚未附 KV 对比结论**。
3. **定界结论**——停在弱 **L2（问题类停点）**：需 hybrid/量化 KV 的 KV 未置零类（不定界到元素/commit）。**L1（检测停点）**：无可检停点（detect=0）。结案：dense 上 FAIL（复现未出现）；对照 S10′ PASS、S07 FAIL+GAP。

## 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格（Origin / 锚点 / overlay / knobs / 期望 detector） |
| `evidence/三层计数.json` | 三层明细（trigger / precision / detect） |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/samples/` | prompt + completion 样本 |


## 上游 PR 关系

| PR / 链接 | 角色 |
|-----------|------|
| [vLLM#43990](https://github.com/vllm-project/vllm/pull/43990) | **根因修复**（KV block 置零相关） |
| [vLLM#47574](https://github.com/vllm-project/vllm/pull/47574) | **同族相关**修复 |
| Ascend `_zero_block_ids` / `AscendKVBlockZeroer` | 平台对照实现（非独立 GitHub PR 钉点） |
