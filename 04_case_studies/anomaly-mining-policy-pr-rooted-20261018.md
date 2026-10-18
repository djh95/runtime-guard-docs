---
cursor:
  subagentId: "bc-fea3f65c-820d-58a1-a9ad-17d3943fe455"
---

# Anomaly mining policy — PR-rooted / typed / low-redundancy (2026-10-18)

**Status:** binding for next mining waves. Supersedes soft-inv density “刷分” practice used through S152.  
**Companion eval:** [`guard-skills-evaluation-pr-weighted-20261018.md`](./guard-skills-evaluation-pr-weighted-20261018.md)  
**Principles still bind:** [`anomaly-principles.md`](./anomaly-principles.md) (origin-faithful; no NaN/`fill_` amplifiers; three-layer rates; HARD/DEFER).

---

## 1. Policy bullets (must follow)

1. **One real fix PR → one root-cause class** (origin-faithful). Prefer a distinct upstream/Ascend fix PR as the credit unit; soft-inverse of that PR is OK **once** for that class.
2. **Stop soft-inv 刷分.** Do **not** mine more ones / zeros / abs / polarity / mag matrix paddings to raise PASS counts or detect %.
3. **Re-mine by PR.** If hard/infra blocked → mark **HARD** (or BLOCKED). Do **not** invent soft-inv substitutes for the same credit.
4. **Group by type** (算子类可归并): RMSNorm / RoPE / Attn / SwiGLU / Residual / Embed·logits·sampler / KV·PD / MoE / Spec / Quant·weight / Overflow·softcap / Other.
5. **Per-type cap:** keep a small representative set (typically **2–4**; KV·PD up to **~6**). Excess soft-inv → **redundant-for-mining** (kept for history / skills regression, **not** next-wave credit).

---

## 2. ABC corpus labels (for eval + mining)

| Label | Meaning | Counts toward Guard-strength headline? | Mining credit? |
|-------|---------|----------------------------------------|----------------|
| **A** | PR-linked / origin-faithful real-class (incl. one soft-inv of that PR) | **Yes** | Yes if under type cap; else redundant-for-mining |
| **B** | Non-redundant type representative (constructed soft-inv OK **once** per type when no PR) | **Yes** | Yes (keeper) |
| **C** | Soft-inv redundancy (ones/zeros/abs/mag/polarity matrix 刷分) | **No** | **No** — freeze |

**Snapshot (PASS inventory through S152 + S08/S10′):** N=141 → **A=18 (12.8%) · B=13 (9.2%) · C=110 (78.0%)**.

---

## 3. Per-type caps + keepers + ones/zeros freeze

| Type | PASS n | Cap | Keepers (mining) | C redundant n | ones/zeros freeze (C) | Cap status |
|------|--------|-----|------------------|---------------|----------------------|------------|
| RMSNorm | 21 | 3 | S26 | 20 | S96, S120, S133, S136, S145, S150, S152 | OK |
| SwiGLU | 21 | 3 | S50 | 20 | S126, S131, S143, S146, S151 | OK |
| Embed·hidden·logits·sampler | 18 | 4 | S43, S46 | 15 | S127, S137, S138 | OK |
| RoPE·positions | 18 | 4 | S40 | 13 | S128, S134, S139, S147 | OK |
| Attn Q/K/V·out | 17 | 4 | S47 | 16 | S130, S132, S141, S142, S148, S149 | OK |
| Residual | 17 | 3 | S31, S48 | 15 | S129, S135, S140, S144 | OK |
| KV·PD·pad | 9 | 6 | S08, S11, S12, S30, S10′ | 3 | S37 | OK |
| Overflow·softcap | 7 | 3 | S33 | 5 | — | OK |
| Quant·weight | 6 | 3 | S23, S24 | 3 | S44 | OK |
| MoE | 5 | 3 | S06, S16, S17 | 0 | — | OK |
| Other | 1 | 2 | S49 | 0 | — | OK |
| Spec | 1 | 2 | S22 | 0 | — | OK |

### Freeze list (ones/zeros soft-inv — do not extend)

S37, S44, S96, S120, S126, S127, S128, S129, S130, S131, S132, S133, S134, S135, S136, S137, S138, S139, S140, S141, S142, S143, S144, S145, S146, S147, S148, S149, S150, S151, S152

Also freeze further **abs / ×÷50 / polarity matrix** clones in C even when not ones/zeros — same redundant-for-mining bucket.

### Spec / GAP / HARD (not PASSed keepers)

| ID | Type | Status | Note |
|----|------|--------|------|
| S01 | KV·PD | FAIL+GAP | garbled finite — detector gap |
| S07 | Quant | FAIL+GAP | W8A8 scale → garbled |
| S45 | Embed/sampler | FAIL+GAP | unique garbage |
| S02/S03/S05/S09/S13 | graph/CP/spec/hybrid | HARD-DEFER | no soft-inv substitute |
| S04 | KV·PD | HARD/DROPPED | HCCN |
| S21 | Spec | HARD | DP+dummy idle |
| S27 | RoPE/MLA | BLOCKED | pe pre-sliced |
| S44 | Quant | INVALID | not skills win |

---

## 4. Typed inventory (PASS)

| ID | Type | PR# | soft-inv? | ones/zeros? | ABC | Mining role |
|----|------|-----|-----------|-------------|-----|-------------|
| S26 | RMSNorm | #42379 | Y | N | A | **KEEP** representative |
| S62 | RMSNorm | — | Y | N | C | redundant-for-mining |
| S66 | RMSNorm | — | Y | N | C | redundant-for-mining |
| S70 | RMSNorm | — | Y | N | C | redundant-for-mining |
| S73 | RMSNorm | — | Y | N | C | redundant-for-mining |
| S77 | RMSNorm | — | Y | N | C | redundant-for-mining |
| S78 | RMSNorm | — | Y | N | C | redundant-for-mining |
| S86 | RMSNorm | — | Y | N | C | redundant-for-mining |
| S87 | RMSNorm | — | Y | N | C | redundant-for-mining |
| S89 | RMSNorm | — | Y | N | C | redundant-for-mining |
| S96 | RMSNorm | — | Y | Y | C | redundant-for-mining (ones/zeros freeze) |
| S100 | RMSNorm | — | Y | N | C | redundant-for-mining |
| S110 | RMSNorm | — | Y | N | C | redundant-for-mining |
| S116 | RMSNorm | — | Y | N | C | redundant-for-mining |
| S120 | RMSNorm | — | Y | Y | C | redundant-for-mining (ones/zeros freeze) |
| S123 | RMSNorm | — | Y | N | C | redundant-for-mining |
| S133 | RMSNorm | — | Y | Y | C | redundant-for-mining (ones/zeros freeze) |
| S136 | RMSNorm | — | Y | Y | C | redundant-for-mining (ones/zeros freeze) |
| S145 | RMSNorm | — | Y | Y | C | redundant-for-mining (ones/zeros freeze) |
| S150 | RMSNorm | — | Y | Y | C | redundant-for-mining (ones/zeros freeze) |
| S152 | RMSNorm | — | Y | Y | C | redundant-for-mining (ones/zeros freeze) |
| S50 | SwiGLU | — | N | N | B | **KEEP** representative |
| S52 | SwiGLU | — | Y | N | C | redundant-for-mining |
| S54 | SwiGLU | — | Y | N | C | redundant-for-mining |
| S56 | SwiGLU | — | Y | N | C | redundant-for-mining |
| S58 | SwiGLU | — | Y | N | C | redundant-for-mining |
| S63 | SwiGLU | — | Y | N | C | redundant-for-mining |
| S67 | SwiGLU | — | Y | N | C | redundant-for-mining |
| S69 | SwiGLU | — | Y | N | C | redundant-for-mining |
| S72 | SwiGLU | — | Y | N | C | redundant-for-mining |
| S76 | SwiGLU | — | Y | N | C | redundant-for-mining |
| S80 | SwiGLU | — | Y | N | C | redundant-for-mining |
| S81 | SwiGLU | — | Y | N | C | redundant-for-mining |
| S103 | SwiGLU | — | Y | N | C | redundant-for-mining |
| S107 | SwiGLU | — | Y | N | C | redundant-for-mining |
| S115 | SwiGLU | — | Y | N | C | redundant-for-mining |
| S121 | SwiGLU | — | Y | N | C | redundant-for-mining |
| S126 | SwiGLU | — | Y | Y | C | redundant-for-mining (ones/zeros freeze) |
| S131 | SwiGLU | — | Y | Y | C | redundant-for-mining (ones/zeros freeze) |
| S143 | SwiGLU | — | Y | Y | C | redundant-for-mining (ones/zeros freeze) |
| S146 | SwiGLU | — | Y | Y | C | redundant-for-mining (ones/zeros freeze) |
| S151 | SwiGLU | — | Y | Y | C | redundant-for-mining (ones/zeros freeze) |
| S10 | Embed·hidden·logits·sampler | #39283,#43741 | N | N | A | redundant-for-mining |
| S43 | Embed·hidden·logits·sampler | — | N | N | B | **KEEP** representative |
| S46 | Embed·hidden·logits·sampler | — | Y | N | B | **KEEP** representative |
| S53 | Embed·hidden·logits·sampler | — | Y | N | C | redundant-for-mining |
| S61 | Embed·hidden·logits·sampler | — | Y | N | C | redundant-for-mining |
| S65 | Embed·hidden·logits·sampler | — | Y | N | C | redundant-for-mining |
| S75 | Embed·hidden·logits·sampler | — | Y | N | C | redundant-for-mining |
| S92 | Embed·hidden·logits·sampler | — | Y | N | C | redundant-for-mining |
| S95 | Embed·hidden·logits·sampler | — | Y | N | C | redundant-for-mining |
| S98 | Embed·hidden·logits·sampler | — | Y | N | C | redundant-for-mining |
| S99 | Embed·hidden·logits·sampler | — | Y | N | C | redundant-for-mining |
| S108 | Embed·hidden·logits·sampler | — | Y | N | C | redundant-for-mining |
| S112 | Embed·hidden·logits·sampler | — | Y | N | C | redundant-for-mining |
| S122 | Embed·hidden·logits·sampler | — | Y | N | C | redundant-for-mining |
| S124 | Embed·hidden·logits·sampler | — | Y | N | C | redundant-for-mining |
| S127 | Embed·hidden·logits·sampler | — | Y | Y | C | redundant-for-mining (ones/zeros freeze) |
| S137 | Embed·hidden·logits·sampler | — | Y | Y | C | redundant-for-mining (ones/zeros freeze) |
| S138 | Embed·hidden·logits·sampler | — | Y | Y | C | redundant-for-mining (ones/zeros freeze) |
| S25 | RoPE·positions | #7082 | Y | N | A | redundant-for-mining (PR soft-inv; type cap) |
| S28 | RoPE·positions | #7341,#7082 | Y | N | A | redundant-for-mining (PR soft-inv; type cap) |
| S40 | RoPE·positions | — | N | N | B | **KEEP** representative |
| S42 | RoPE·positions | — | N | N | C | redundant-for-mining |
| S57 | RoPE·positions | — | Y | N | C | redundant-for-mining |
| S79 | RoPE·positions | — | Y | N | C | redundant-for-mining |
| S82 | RoPE·positions | — | Y | N | C | redundant-for-mining |
| S84 | RoPE·positions | — | Y | N | C | redundant-for-mining |
| S85 | RoPE·positions | — | Y | N | C | redundant-for-mining |
| S101 | RoPE·positions | — | Y | N | C | redundant-for-mining |
| S102 | RoPE·positions | — | Y | N | C | redundant-for-mining |
| S104 | RoPE·positions | #7082 | Y | N | A | redundant-for-mining (PR-linked soft-inv; RoPE cap) |
| S105 | RoPE·positions | #7082 | Y | N | A | redundant-for-mining (PR-linked soft-inv; RoPE cap) |
| S113 | RoPE·positions | — | Y | N | C | redundant-for-mining |
| S128 | RoPE·positions | — | Y | Y | C | redundant-for-mining (ones/zeros freeze) |
| S134 | RoPE·positions | — | Y | Y | C | redundant-for-mining (ones/zeros freeze) |
| S139 | RoPE·positions | — | Y | Y | C | redundant-for-mining (ones/zeros freeze) |
| S147 | RoPE·positions | — | Y | Y | C | redundant-for-mining (ones/zeros freeze) |
| S47 | Attn Q/K/V·out | — | N | N | B | **KEEP** representative |
| S51 | Attn Q/K/V·out | — | Y | N | C | redundant-for-mining |
| S59 | Attn Q/K/V·out | — | Y | N | C | redundant-for-mining |
| S60 | Attn Q/K/V·out | — | Y | N | C | redundant-for-mining |
| S68 | Attn Q/K/V·out | — | Y | N | C | redundant-for-mining |
| S83 | Attn Q/K/V·out | — | Y | N | C | redundant-for-mining |
| S109 | Attn Q/K/V·out | — | Y | N | C | redundant-for-mining |
| S111 | Attn Q/K/V·out | — | Y | N | C | redundant-for-mining |
| S114 | Attn Q/K/V·out | — | Y | N | C | redundant-for-mining |
| S117 | Attn Q/K/V·out | — | Y | N | C | redundant-for-mining |
| S118 | Attn Q/K/V·out | — | Y | N | C | redundant-for-mining |
| S130 | Attn Q/K/V·out | — | Y | Y | C | redundant-for-mining (ones/zeros freeze) |
| S132 | Attn Q/K/V·out | — | Y | Y | C | redundant-for-mining (ones/zeros freeze) |
| S141 | Attn Q/K/V·out | — | Y | Y | C | redundant-for-mining (ones/zeros freeze) |
| S142 | Attn Q/K/V·out | — | Y | Y | C | redundant-for-mining (ones/zeros freeze) |
| S148 | Attn Q/K/V·out | — | Y | Y | C | redundant-for-mining (ones/zeros freeze) |
| S149 | Attn Q/K/V·out | — | Y | Y | C | redundant-for-mining (ones/zeros freeze) |
| S31 | Residual | — | N | N | B | **KEEP** representative |
| S48 | Residual | — | N | N | B | **KEEP** representative |
| S55 | Residual | — | Y | N | C | redundant-for-mining |
| S64 | Residual | — | Y | N | C | redundant-for-mining |
| S88 | Residual | — | Y | N | C | redundant-for-mining |
| S90 | Residual | — | Y | N | C | redundant-for-mining |
| S91 | Residual | — | Y | N | C | redundant-for-mining |
| S93 | Residual | — | Y | N | C | redundant-for-mining |
| S94 | Residual | — | Y | N | C | redundant-for-mining |
| S97 | Residual | — | Y | N | C | redundant-for-mining |
| S106 | Residual | — | Y | N | C | redundant-for-mining |
| S119 | Residual | — | Y | N | C | redundant-for-mining |
| S125 | Residual | — | Y | N | C | redundant-for-mining |
| S129 | Residual | — | Y | Y | C | redundant-for-mining (ones/zeros freeze) |
| S135 | Residual | — | Y | Y | C | redundant-for-mining (ones/zeros freeze) |
| S140 | Residual | — | Y | Y | C | redundant-for-mining (ones/zeros freeze) |
| S144 | Residual | — | Y | Y | C | redundant-for-mining (ones/zeros freeze) |
| S08 | KV·PD·pad | — | N | N | B | **KEEP** representative |
| S10′ | KV·PD·pad | APC recycle | N | N | A | **KEEP** representative |
| S11 | KV·PD·pad | #18798 | N | N | A | **KEEP** representative |
| S12 | KV·PD·pad | #50276 | N | N | A | **KEEP** representative |
| S30 | KV·PD·pad | #39444 | Y | Y | A | **KEEP** representative |
| S32 | KV·PD·pad | #7144 | Y | N | A | redundant-for-mining (PR soft-inv; type cap) |
| S34 | KV·PD·pad | — | N | N | C | redundant-for-mining |
| S35 | KV·PD·pad | — | N | N | C | redundant-for-mining |
| S37 | KV·PD·pad | — | N | Y | C | redundant-for-mining (ones/zeros freeze) |
| S20 | Overflow·softcap | #56579 | N | N | A | redundant-for-mining (Overflow; softcap class) |
| S29 | Overflow·softcap | — | Y | N | C | redundant-for-mining |
| S33 | Overflow·softcap | — | N | N | B | **KEEP** representative |
| S36 | Overflow·softcap | — | N | N | C | redundant-for-mining |
| S38 | Overflow·softcap | — | N | N | C | redundant-for-mining |
| S39 | Overflow·softcap | — | N | N | C | redundant-for-mining |
| S41 | Overflow·softcap | — | N | N | C | redundant-for-mining |
| S14 | Quant·weight | #9687 | N | N | A | redundant-for-mining (Quant; prefer S23/S24 reps) |
| S23 | Quant·weight | — | N | Y | B | **KEEP** representative |
| S24 | Quant·weight | — | N | Y | B | **KEEP** representative |
| S44 | Quant·weight | — | N | Y | C | redundant-for-mining (ones/zeros freeze) |
| S71 | Quant·weight | — | Y | N | C | redundant-for-mining |
| S74 | Quant·weight | — | Y | N | C | redundant-for-mining |
| S06 | MoE | — | N | N | B | **KEEP** representative |
| S16 | MoE | #16189,#38989 | Y | N | A | **KEEP** representative |
| S17 | MoE | #9036,#43769 | Y | N | A | **KEEP** representative |
| S18 | MoE | #16245,#16550 | Y | N | A | redundant-for-mining (PR-linked; MoE saturated) |
| S19 | MoE | #9692 | Y | N | A | redundant-for-mining (PR-linked; MoE saturated) |
| S49 | Other | — | N | N | B | **KEEP** representative |
| S22 | Spec | #18657 | N | N | A | **KEEP** representative |

---

## 5. Next mining backlog (no ones/zeros fillers)

Re-mine **by real PR**; blocked → **HARD**. Sources: [`anomaly-candidate-bugs-20261017.md`](./anomaly-candidate-bugs-20261017.md), older wave docs.

### By type — actionable / HARD

| Type | Next real PR / item | Tag | Easy/HARD | Blocker / note |
|------|---------------------|-----|-----------|----------------|
| **Attn** | vLLM#56579 softcap NaN (class; S20 was constructed) | both? | HARD | Gemma softcap weights |
| **Attn** | ascend#18068 FA3 mixed prefill/spec | ascend-only | HARD | FA3 + RL flag |
| **Attn** | ascend#17925 non-PA FIA K/V contiguous | ascend-only | maybe later | need natural non-contig trigger |
| **Graph/pad** | ascend#18750 Engram FULL graph pad | ascend-only | HARD | Engram weights |
| **Graph/pad** | S02 (#37442 family) | both | HARD-DEFER | already parked |
| **Spec** | S05 rejection NaN paths | both | HARD-DEFER | no amp |
| **Spec** | vLLM#56734 / S21 dummy stale | both | HARD | Spec+DP idle |
| **Scheduler** | ascend#18207 + vLLM#49675 deferred-free preempt | both | HARD | hang/progress detect |
| **Quant** | vLLM#58032 FP8 UE8M0; AWQ/GPTQ | both? | HARD | lab FP8 / no AWQ |
| **Quant** | S07 detector only | both | GAP | garbled detector — **not** new overlay |
| **KV·PD** | type near cap — prefer unpark HARD S02/S03 only with knobs | — | HARD | no soft-inv pad |
| **MoE** | **STOP** — saturated (S06/S16–S19) | — | — | no more MoE ∩ |
| **RoPE / RMSNorm / SwiGLU / Residual / Attn soft-inv matrix** | **STOP 刷分** | — | — | C freeze |
| **garbled-GAP** | detector work S01/S07/S45 | — | eng | **priority #1 for Guard**, not mining |

### Explicitly do **not** mine next

- Any new ones_like / zeros_like / abs / ×÷N polarity clones on RMSNorm / Residual / SwiGLU / Attn / RoPE / logits.
- Soft-inv substitutes for HARD credits (S02/S04/S05/S21/…).
- More MoE router/combine variants.

---

## 6. Ops notes

- No new overlays on host **160** under this policy refresh (eval/docs only).
- Skills regression may still **replay** C evidence; do not treat new C PASSes as mining wins.
- Dual-push docs/test mains when policy text lands in `runtime-guard-docs`.
