# WHY_UNDETECTED — S45 topk_bottom_keep

- **Anomaly reproduced?** YES (precision) — origin-faithful top-k/top-p on `-logits` (direction flip); **not** an amplifier
- **Type:** unique mixed-script / garbage completions (finite; no NaN/Inf)
- **Trigger:** ANOMALY_TRIGGER S45 topk_bottom_keep (trigger=16)
- **Layers:** trigger=16 · precision=**unique** (score `precision_hits=47/48`, `unique=48`; identical-mode undercounts → layers.json `precision=0`) · detect=**0**
- **Detector:** `token_repeat` + `logits_finite` armed — **both missed**
  - outputs are diverse unique garbage (not digit/`!!!!` collapse) → `token_repeat` weak
  - logits remain finite → `logits_finite` miss
- **Gap:** same class as S01/S07 — need garbled / mixed-script / unique-garbage detector; do **not** invent NaN/fill to fake PASS
- **Classification:** **FAIL + GAP** (real precision + detector miss). Not INVALID.
- **Samples (≥3):** `samples/c_000.json`, `c_002.json`, `c_003.json` (+ 44 more `garbage_mixed_script`)
  - c_000: `*angstrom ')\r\n mfronetogroupIBETerrain …颇有ATES将进一步+<//books…`
  - c_002: `PropertyParamsagnartre厖())\r\n丝丝 Benchmark/msgETY…`
  - c_003: `CallCheckمناطأوضاع米兰إبد*X,’”-peerrangle…`
- **Score:** `label_counts={'garbage_mixed_script':44, 'repeat':22, …}`; `identical_across_requests=False`
- **Contrast:** S46 penalty-sign-flip → digit/`1.1.1…` collapse → `token_repeat` PASS; do not retune S45 into amplifier shopping
