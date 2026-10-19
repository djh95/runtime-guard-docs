# WHY_UNDETECTED — S07 quant_scale_collapse

- **Anomaly reproduced?** YES (precision)
- **Type:** W8A8 dequant scale collapse → identical mixed-script garbage completions
- **Trigger:** ANOMALY_TRIGGER S07 zero+1e20 on deq_scale (thousands of events)
- **Detector:** logits_finite armed — **missed** (outputs finite; no NaN/Inf)
- **Gap:** need garbage/semantic detector or scale-integrity check; token_repeat also weak on diverse garbage
- **Samples:** samples/completion_*.json (identical across requests)
