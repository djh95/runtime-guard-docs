# WHY — S01 kv_block_nonzero（复判）

- **结案：** **FAIL（复现未出现）** / repro-blocked（不是 FAIL+GAP）。**主结论保留。**
- **异常是否复现？** 稠密 bf16 上：**否**（可见 completion 通顺；CJK 排除后 precision=0）。
- **precision 误标：** 旧 136/25/0 的 25、以及复判 runner 虚报，均为 CJK 启发式误计；排除后 **0**。
- **patch 入口未切换：** 162 canonical 残缺 patch（≈28 行/1 文件）未切到满量 overlay（251 行/5 文件）；残缺入口下 trigger 可恒 0。满量入口能刷 trigger，仍无坏输出。
- **Trigger：** 有（复判 154：synth_block0 / skip_zero_upstream / force_should_init）。详见 trigger_excerpt.txt。
- **Detect：** 0——本轮无可检坏输出，谈不上「乱码检测漏检」结案。
- **形态：** origin 要 hybrid/量化 KV；160 上 `--kv-cache-dtype fp8` 因 `FP8_ATTENTION` assert 起服失败。
- **对照：** S10′ keep-set 160 仍为 PASS **65 / 20 / 79**（`token_repeat`）。
- **样本：** samples/ 下带 `prompt` + `completion`。
