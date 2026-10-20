# WHY — S01 kv_block_nonzero（复现未出现，非 undetected 漏检）

- **结案：** **FAIL（复现未出现）** / repro-blocked（不是 FAIL+GAP）。
- **异常是否复现？** 稠密 bf16 上：**否**（可见 completion 通顺；CJK 排除后 precision=0）。
- **三层（160 复判）：** trigger=**154** · precision=**0** · detect=**0**。旧 precision=25 为 CJK 启发式误计。
- **形态：** origin 要 hybrid/量化 KV；本 pin 上 `--kv-cache-dtype fp8` 因 `FP8_ATTENTION` assert 起服失败。
- **对照：** S10′ = PASS **65 / 20 / 79**（`token_repeat`）；S07 = FAIL+GAP（有乱码+漏检）。本包不是漏检族。
- **样本：** `samples/` 下带 `prompt` + `completion`。
