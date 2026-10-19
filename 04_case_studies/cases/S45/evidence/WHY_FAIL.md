# S45 FAIL topk_bottom_keep

- Overlay is origin-faithful (filter on -logits) — NOT an amplifier.
- trigger=16, unique-garbage precision, detect=0 (no local re-reads / nonfinite).
- Parked **FAIL + GAP** (detector miss on unique garbage). Not INVALID.
- See [`WHY_UNDETECTED.md`](./WHY_UNDETECTED.md) + ≥3 samples under `samples/`.
