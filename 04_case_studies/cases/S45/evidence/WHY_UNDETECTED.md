# WHY_UNDETECTED — S45 topk_bottom_keep

- **异常是否复现？** 是（precision）——origin-faithful 的 top-k/top-p 作用在 `-logits`（方向翻转）；**不是**放大器。
- **类型：** unique 混合脚本 / garbage completion（finite；无 NaN/Inf）。
- **Trigger：** `ANOMALY_TRIGGER` S45 topk_bottom_keep（trigger=16）。
- **三层：** trigger=16 · precision=**unique**（score `precision_hits=47/48`，`unique=48`；identical-mode undercount → layers.json `precision=0`）· detect=**0**。
- **Detector：** `token_repeat` + `logits_finite` 均已武装，**都 miss**。
  - 输出是多样 unique garbage（不是 digit / `!!!!` 塌缩）→ `token_repeat` 偏弱
  - logits 仍有限 → `logits_finite` miss
- **缺口：** 与 S01 / S07 同类——需要 garbled / mixed-script / unique-garbage detector；**不要**用 NaN / fill 伪造 PASS。
- **归类：** **FAIL + GAP**（真实 precision + detector miss）。不是 INVALID。
- **样本（≥3）：** `samples/c_000.json`、`c_002.json`、`c_003.json`（另有 44 个 `garbage_mixed_script`）
  - c_000：`*angstrom ')
 mfronetogroupIBETerrain …颇有ATES将进一步+<//books…`
  - c_002：`PropertyParamsagnartre厖())
丝丝 Benchmark/msgETY…`
  - c_003：`CallCheckمناطأوضاع米兰إمد*X,’”-peerrangle…`
- **Score：** `label_counts` 含 `garbage_mixed_script:44`、`repeat:22` 等；`identical_across_requests=False`
- **对照：** 不要把 S45 调成 amplifier shopping；能检的采样 soft-inv 另案处理。
