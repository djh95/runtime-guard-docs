# WHY_UNDETECTED — S45 topk_bottom_keep

- **异常是否复现？** 是（precision）——origin-faithful 的 top-k/top-p 作用在 `-logits`（方向翻转）；**不是**放大器。
- **类型：** 各不相同乱码（有限；无 NaN/Inf）。
- **Trigger：** `ANOMALY_TRIGGER` S45 topk_bottom_keep（trigger=16）。
- **三层（二次盲跑现行）：** trigger=16 · precision=4 · detect=**0**。
- **Detector：** `token_repeat` + `logits_finite` 均已武装，**都 miss** → **乱码检测漏检**。
- **复现要点：** **双树写入**（Ascend B + canonical vllm sampler）+ **temp=0.8**（勿用 0）。
- **首轮盲跑：** 缺双树 / temp=0 → 对不上；二次盲跑对齐后 **漏检精确复现**（仍 GAP）。
- **归类：** **FAIL + GAP**。不是 INVALID。
- **样本：** `samples/` 下各不相同混合脚本垃圾；内容相同计分会低估。
- **对照：** 能检对照 S43；不要 amplifier shopping。
