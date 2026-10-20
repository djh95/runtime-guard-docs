# WHY — S01 kv_block_nonzero（复判）

- **结案：** **FAIL（复现未出现）** / repro-blocked（不是 FAIL+GAP）。
- **异常是否复现？** 稠密 bf16 上：**否**（可见 completion 通顺；CJK 排除后 precision=0）。旧 precision=25 为中文误报。
- **Trigger：** 有（复判 154：synth_block0 / skip_zero_upstream / force_should_init）。详见 trigger_excerpt.txt。
- **Detect：** 0——本轮无可检坏输出，谈不上「乱码检测漏检」结案。
- **形态：** origin 要 hybrid/量化 KV；160 上 `--kv-cache-dtype fp8` 因 `FP8_ATTENTION` assert 起服失败。
- **对照：** S10′ keep-set 160 仍为 PASS **65 / 20 / 79**（`token_repeat`）。
- **样本：** samples/ 下带 `prompt` + `completion`。
