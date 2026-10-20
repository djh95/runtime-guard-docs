# S45 FAIL — topk_bottom_keep

- Overlay 是 origin-faithful（在 `-logits` 上做 filter），**不是**放大器。
- 现行三层：**16 / 4 / 0**（二次盲跑；乱码检测漏检）。
- 归档为 **FAIL + GAP**。不是 INVALID。
- 详见 [`WHY_UNDETECTED.md`](./WHY_UNDETECTED.md)，以及 `samples/`。
