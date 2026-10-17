# Older-PR mine wave-2 — S29/S30/S31 (2026-10-17)

After S25/S26/S28, skipped S27-class MLA pe no-ops. Landed three distinct easy PASS on 160 (G2 `f2aefd068`):

| ID | Root cause | Layers | Cards | Detector |
|----|------------|--------|-------|----------|
| S29 | Logits fp16 demote (sampling/cast) | 132/14/48 | 2,3 | token_repeat |
| S30 | Null-block KV dirt (#39444 soft-inv) | 2/14/48 | 2,3 | token_repeat |
| S31 | RMSNorm residual drop ≠ S26 | 470/48/48 | 12,13 | token_repeat |

Protocol: origin-faithful overlays; no force-NaN / token fill; three-layer rates. Skills inbox updated for S29–S31. Builder IDLE. Still open: graph pad #7144, softcap/FP8/FA3 weights, S21 dummy trig=0.
