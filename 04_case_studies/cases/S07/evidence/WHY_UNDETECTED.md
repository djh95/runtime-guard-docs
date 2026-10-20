# WHY_UNDETECTED — S07 quant_scale_collapse

- **异常是否复现？** 是（precision）。
- **类型：** W8A8 dequant scale collapse → 多次请求输出同一段混合脚本乱码。
- **Trigger：** `ANOMALY_TRIGGER` S07（`deq_scale` 上 zero+1e20，事件数千级）。
- **Detector：** 已武装 `logits_finite`，但 **miss**——输出有限，没有 NaN/Inf。
- **缺口：** 需要 garbage / 语义 detector，或 scale 完整性检查；多样 garbage 上 `token_repeat` 也偏弱。
- **样本：** `samples/completion_*.json`（跨请求内容相同）。
