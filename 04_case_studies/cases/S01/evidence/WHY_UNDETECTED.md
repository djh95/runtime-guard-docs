# WHY_UNDETECTED — S01 kv_block_nonzero

- **异常是否复现？** 按当时 precision 记账为「是」，但可见样本表明 precision 很可能是中文误报；稠密栈上更常见「只有 trigger、没有坏输出」。
- **类型：** skip KV block zeroing → 预期混合脚本 garbage（origin 在 hybrid/量化 KV）。
- **Trigger：** synth_block0 + skip_zero_upstream（约 136）。详见 trigger_excerpt.txt。
- **Detector：** 已武装 `logits_finite`，**miss**（有限输出抓不住）。
- **缺口：** 需要 garbage / 语义类 detector；`logits_finite` 只抓 NaN/Inf。
- **样本：** samples/ 下带 `prompt` + `completion`；当前可见 completion 为通顺散文。
