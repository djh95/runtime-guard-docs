# S45 FAIL — topk_bottom_keep

- Overlay 是 origin-faithful（在 `-logits` 上做 filter），**不是**放大器。
- trigger=16；precision 侧是 unique garbage；detect=0（没有 local re-reads / nonfinite）。
- 归档为 **FAIL + GAP**（detector miss on unique garbage）。不是 INVALID。
- 详见 [`WHY_UNDETECTED.md`](./WHY_UNDETECTED.md)，以及 `samples/` 下不少于 3 个样本。
