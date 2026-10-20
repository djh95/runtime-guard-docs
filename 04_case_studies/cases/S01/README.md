# S01 · KV skip-zero → logits 有限乱码（detector GAP）

这是一份公开、自洽的案例包：只靠本目录材料就能读完。

同族里能检出来的对照包：[S10′（S10p）](../S10p/)。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **FAIL+GAP**（repro_mode=`origin_tuned`） |
| 三层率 | **136 / 25 / 0**（trigger / precision / detect） |
| 期望 detector | `logits_finite`（miss） |
| Guard pin | G2 · `f2aefd068c4bd299d91cf0a1fdf642a3f327308f` |
| 模型 | Qwen3-8B · TP2 |
| 上游锚 | [vLLM#43990](https://github.com/vllm-project/vllm/pull/43990) · [#47574](https://github.com/vllm-project/vllm/pull/47574) |
| Origin | `both` |

## 1 · 现象

服务仍返回 200。logits（采样前的分值）始终是有限数，没有 NaN/Inf；文字仍可能是乱码或中英混杂的垃圾，故 `logits_finite` 漏检——或者在**错误评分**下，被记成 garbage。

本包能直接打开的样本见 [evidence/samples/](./evidence/samples/)。可见文本是通顺的中英散文（华为 NPU / vLLM 介绍），**并不是**乱码。按排除 CJK 后的评分，应标成普通中英混合，而不是 `garbage_mixed_script`。

那为什么还留这个案例？归档 `status.json` 写过 `precision_hits=25` 和一串 `garbage_mixed_script:completion_*.json` 文件名，那些 completion **没有随本包落盘**。案例要讲清两件事：

1. **logits 数值有限仍可能是乱码**：logits（采样前的分值）没有 NaN/Inf 时 `logits_finite` 不报警，这是 detector 缺口（复读窗也盖不住这类症状）。
2. **当时的 precision 不能直接当成「乱码已复现」的铁证**——多半是把正常中文误判成异常。

真实的跨请求相同乱码见同缺口族 **S07**；同大类能被抓住的是 **S10′** 的 recycle-zero。

## 2 · 根因

| 字段 | 值 |
|------|-----|
| Origin | `both`（vLLM 与 Ascend 同失败模式） |
| 语义 | 新分配 KV block **未置零** → 读脏页 |
| 典型栈 | **hybrid / 量化 KV**（不是任意稠密 bf16） |

上游：[#43990](https://github.com/vllm-project/vllm/pull/43990)、[#47574](https://github.com/vllm-project/vllm/pull/47574)；Ascend 对照 `_zero_block_ids` / `AscendKVBlockZeroer`。

完整 overlay（约 251 行 / 5 文件）会：强制 `needs_kv_cache_zeroing`；skip `zero_block_ids`；并在 dense 路径做 **synth_block0**。synth_block0 抬高的是 **trigger 日志**，不等于已经读到脏 KV 乱码。早期残缺 overlay（2 文件 / +18 行）连路径都不完整。

## 3 · Guard 结果与缺口

归档启用 `logits_finite`（`item_sync`）。三层摘自 [evidence/layers.json](./evidence/layers.json) / [status.json](./evidence/status.json)：

| 层 | 数 | 含义 |
|----|---:|------|
| trigger | **136** | `ANOMALY_TRIGGER`（skip_zero / synth_block0） |
| precision | **25** | 旧启发式；笔记几乎全是 `garbage_mixed_script:…`（CJK 误计可疑） |
| detect | **0** | 无 `report_*.json`；`logits_finite` miss |

缺口类型：logits 数值有限、文字却是乱码 / 跨请求相同 junk——现网无专用 detector。trigger=136 说明注入路径在跑。对照：S10′ recycle → `token_repeat` PASS；S01 → 漏检。

证据分组见 [evidence/EVIDENCE_GROUPS.md](./evidence/EVIDENCE_GROUPS.md)。

## 4 · 复现：当时 vs 现在

**结论：** 当初 precision=25 很大概率是把正常中文计成 garbage；真·脏 KV 要 **hybrid / 量化 KV**。稠密 bf16 + synth_block0 多半只刷 trigger、不易出坏输出——与后来 dense 多轮 0 bad 不矛盾。

| 维 | 当时（归档 · 2026-10-16） | 现在（稠密 bf16 复核） |
|----|-------------------------|-------------------------|
| KV 形态 | SPEC 要求 hybrid / 量化 | 稠密 bf16（无 FP8/hybrid 页语义） |
| 三层 | 136 / 25 / 0 | trigger 或有；**0 坏输出**；detect 0 |
| 可见样本 | 通顺散文 | 无乱码样本 |
| 评分 | `ord>127` 把中文算 weird | 应排除 CJK；散文 ≠ garbage |

若要真复现 origin：用 hybrid/量化 KV（或当时同形态栈），并归档带 **prompt + completion** 的原始样本。dense + synth 只适合验证 trigger 路径。

## 5 · 学完能做什么

1. 会判断：logits（采样前的分值）始终是有限数、没有 NaN/Inf 时，`logits_finite` 漏检，但文字仍可能是乱码。
2. 会分开看三层计数：trigger ≠ precision ≠ detect；中间「25」还可能被评分污染。
3. 会对照 S10′：同属 KV 脏读，recycle 能检；skip-zero 时 logits（采样前的分值）有限、文字仍乱码，会漏检。
4. 会核对环境：dense+synth 只证明路径打中，不等于已经读到脏 KV 乱码；不要用强制 NaN / 填复读 token 造症状。
5. 公开案例材料写全再对外；空壳页不够用。

产品侧 detector GAP（garbled-text / cross-request-identical）另开任务，本包不承诺时间表。

## 证据目录

[evidence/](./evidence/) — 含多组 sample、trigger 摘录、report 空目录说明、precision 中文误报核对。
