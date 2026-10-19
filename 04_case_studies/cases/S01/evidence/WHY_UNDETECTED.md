# WHY_UNDETECTED — S01 kv_block_nonzero

- **Anomaly reproduced?** YES (precision)
- **Type:** skip KV block zeroing → mixed-script garbage completions
- **Trigger:** synth_block0 + skip_zero_upstream (ANOMALY_TRIGGER ~136)
- **Detector:** logits_finite armed — **missed** (garbage is finite)
- **Gap:** need garbage/semantic detector; logits_finite only catches NaN/Inf
- **Samples:** samples/completion_*.json (garbage_mixed_script)
