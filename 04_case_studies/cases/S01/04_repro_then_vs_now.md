# 4 · 复现：Then vs Now

> 结论先说：**当初「precision=25」很大概率是把正常中文计成 garbage 的误计；真·脏 KV 形态要 hybrid/量化 KV。dense bf16 + synth_block0 只会刷 trigger、不易出坏输出——与后来 dense 多轮 0 bad 不矛盾。**

## 对照

| 维 | Then（FE 顶层 · 2026-10-16） | Now（dense bf16 复核叙事） |
|----|------------------------------|----------------------------|
| KV 形态 | SPEC 要求 **hybrid / 量化** | **稠密 bf16**（无 FP8/hybrid 页语义） |
| Overlay | 满量 ~251 行 / 5 文件；或早期残缺 2 文件 | 残缺则路径不全；满量仍难脏读 |
| 三层 | 136 / 25 / 0 | trigger 或有；**0 bad**；detect 0 |
| 可见样本 | `sample_01` = 通顺散文 | 无汤样 |
| 评分 | 旧启发式：`ord>127` 比例 → 中文易误判 garbage | 现 scorer：普通 CN+EN → `mixed_script`；汤才 `garbage_mixed_script` |

## precision=25 为何可疑

旧 `run_anomaly_repro.sh` 启发式把 **CJK 码点 > 127** 算进 weird；正常中文段 weird 比可 >0.35 → 标成 `garbage_mixed_script`。对归档 `sample_01` 用该逻辑会误杀。  
后修评分已排除 CJK；对本包样本应判 **mixed_script / 非 soup**。

因此：**136 可信（触发日志）；25 不可信（CJK 误计）；0 detect 可信。**

## 现在断在哪

1. **形态错配** — origin 在 hybrid/FP8 页；dense bf16 不同。  
2. **synth_block0 假触发** — 抬 trigger、输出仍可正常。  
3. **若 overlay 残缺** — 连 skip 都不完整（早期 `T105627`/`T110349`）。  
4. **评分已校正** — 不必假设栈「免疫」了一个曾铁证汤；更可能是当时 precision 虚高。

若要真复现 origin：用 **hybrid/量化 KV**（或当时同形态栈），并归档 **原始 completion JSON**；dense+synth 只验证 trigger 路径。
