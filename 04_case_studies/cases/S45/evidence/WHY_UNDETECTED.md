# WHY — S45 topk_bottom_keep（FAIL+GAP）

- **结案：** **FAIL+GAP**（异常已出现；detector miss）。不是 INVALID。
- **异常是否复现？** 是——origin-faithful 的 top-k/top-p 作用在 `-logits`（方向翻转）；**不是**放大器。
- **类型：** 各不相同乱码（有限；无 NaN/Inf）。
- **三层（现行）：** trigger=**16** · precision=**4** · detect=**0**。
- **Detector：** `token_repeat` + `logits_finite` 均已武装，**都 miss** → 乱码检测漏检。
- **复现要点：** **双树写入**（Ascend B + canonical vllm sampler）+ **temp=0.8**（勿用 0）→ 按复现技巧复现后仍为 detect=0。
- **样本：** `samples/` 下各不相同混合脚本垃圾；内容相同计分会低估。
- **对照：** 能检对照 S43；乱码样板对照 S07；S01 是复现未出现（非乱码样板）。勿 amplifier shopping。
