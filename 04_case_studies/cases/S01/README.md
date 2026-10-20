# S01 · KV skip-zero → FAIL（复现未出现）

这是一份公开、自洽的案例包：只靠本目录材料就能读完。

同族里**能检出来**的对照包：[S10′（S10p）](../S10p/)（recycle-zero → `token_repeat` PASS）。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案结论 | **FAIL（复现未出现）** / repro-blocked |
| 三层率（2026-10-20 160 复判） | **154 / 0 / 0**（trigger / precision〔CJK 排除后〕/ detect） |
| 旧归档三层 | 136 / 25 / 0（precision=25 为 CJK 误计，不可当真坏输出） |
| 期望 detector | 乱码类；本轮**无可检坏输出**，故不构成 FAIL+GAP |
| Guard pin | G2 · `f2aefd068c4bd299d91cf0a1fdf642a3f327308f` |
| 模型 | Qwen3-8B · TP2 · 稠密 float16 |
| 上游锚 | [vLLM#43990](https://github.com/vllm-project/vllm/pull/43990) · [#47574](https://github.com/vllm-project/vllm/pull/47574) |
| Origin | `both` |

## 1 · 现象

Overlay 打上后服务仍 200。可见 completion 是通顺中英散文（华为 NPU / vLLM 介绍），**不是**乱码。样本见 [evidence/samples/](./evidence/samples/)。

旧跑把 `ord(c)>127` 的中文算 weird，于是记成 `garbage_mixed_script`×N；排除 CJK 后 weird≈0 → **precision 应记 0**。没有坏输出时，**不要**写成 FAIL+GAP。

同族对照：**S10′** 在同一 pin 上能打出复读/`xxxx` 并被 `token_repeat` 抓住（keep-set 160：**65 / 20 / 79**）。真·跨请求内容相同的乱码见 **S07**。

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
| precision | **0** | CJK 排除后；旧启发式会虚报 25 |
| detect | **0** | 无 `report_*.json` |

对照：**S10′** = 有坏输出 + detect；**S01 dense** = 只有 trigger。证据分组见 [evidence/EVIDENCE_GROUPS.md](./evidence/EVIDENCE_GROUPS.md)。

## 4 · 复现：形态前提

| 维 | 要求 / 实测 |
|----|-------------|
| Origin 形态 | SPEC：**hybrid / 量化 KV** |
| 160 dense（本复判） | Qwen3-8B float16 + 满量 overlay · cards `4,5` · `PRODUCT_TREE=B` → **0 坏输出** |
| 162 dense（此前） | 七轮满量 overlay / 脏 HBM / 缩池 → **0 坏输出** |
| hybrid/fp8 一次尝试 | `--kv-cache-dtype fp8` → Ascend `FP8_ATTENTION` 能力 assert，**起服失败**；不夸大、不另造放大器 |

若要真复现 origin：在**支持量化/hybrid KV**的栈上跑，并归档带 **prompt + completion** 的原始坏样本。dense + synth 只适合验证 trigger 路径。

## 5 · 别人按包能核对什么

1. 会把「有 trigger」和「有坏输出」分开：本包 dense 复判只有前者。
2. 会用排除 CJK 的评分看样本：通顺中文 ≠ `garbage_mixed_script`。
3. 会对照 S10′：同属 KV 脏读族，recycle 能检；S01 在稠密栈上复现未出现。
4. 会核对形态：hybrid/量化 KV 是前提；本机 fp8 KV 被硬件能力门挡住时如实记 blocker。
5. 没有坏输出时不写 FAIL+GAP。

## 证据目录

[evidence/](./evidence/) — 复判 sample（prompt+completion）、trigger 摘录、CJK 核对、report 空目录说明。
