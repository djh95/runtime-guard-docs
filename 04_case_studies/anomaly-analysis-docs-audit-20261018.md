---
cursor:
  subagentId: "bc-fea3f65c-820d-58a1-a9ad-17d3943fe455"
---

# Anomaly analysis-docs audit — S01–S152 (2026-10-18)

**Question:** Are per-anomaly analysis documents all complete?  
**Answer: No.**

| Category | Count | Share |
|----------|------:|------:|
| **1 Fully documented** | **142** | 93.4% |
| **2 Evidence-only / thin** | **1** | 0.7% |
| **3 Missing / stub / HARD unrun** | **9** | 5.9% |
| **Total** | **152** | 100% |
| Of which **C soft-inv** (all in cat1) | **110** | — |

**Sources checked:** Project `anomaly-fail-evidence/` + test-repo `fail-evidence/`；`anomaly-skills-capability-20261017.md`；`anomaly-skills-runs/` (+ `batch-pass-wave-20261017.md`)；SKILLS_METADATA / living capability & eval docs. **No new mining.**

---

## Definition of “complete”

Enough offline analysis for **symptoms + repro notes + skills bound depth**:

| Bar | Requirement |
|-----|-------------|
| **Minimum (used for cat1)** | Capability matrix row **and** (`WHY_PASS` / `WHY_UNDETECTED` / `WHY_INVALID` **or** skills-run / batch case-study entry) |
| **Fully (cat1)** | Minimum + meaningful WHY (root `WHY_PASS` or GAP `WHY_UNDETECTED`) + skills-run **or** early-wave batch writeup |
| **Evidence-only (cat2)** | Some FE / nested notes + capability, but **no** solid WHY_PASS and/or no dedicated writeup |
| **Missing (cat3)** | HARD/未跑/skip with little more than a capability stub |

C bucket scenarios are still **reported** (they are documented for skills regression) but remain **redundant-for-mining** per policy.

---

## 1. Fully documented — 142

Includes: almost all PASS S06–S152 with WHY_PASS + capability + skills-run (S20+ individual runs; early MoE/KV often via `batch-pass-wave-20261017.md`); GAP **S01 / S07 / S45** with `WHY_UNDETECTED` + runs; INVALID **S44** with `WHY_INVALID` + run.

**C soft-inv (110):** all land in cat1 (WHY_PASS + capability + skills-run v4.x–v5.8). Status = documented, **not** mining credit.

---

## 2. Evidence-only / thin — 1

| ID | Kind | Issue |
|----|------|-------|
| **S08** | PASS | FE only has nested historical `WHY_UNDETECTED` (early attempts); **no root `WHY_PASS.md`**; **no** `S08-*.md` skills-run (mentioned in batch wave only); capability row OK |

---

## 3. Missing / stub / HARD unrun — 9

| ID | Kind | Notes |
|----|------|-------|
| S02 | HARD-DEFER | graph pad — capability stub only |
| S03 | HARD-DEFER | CP slot |
| S04 | HARD / DROPPED | PD / HCCN |
| S05 | HARD-DEFER | spec rejection NaN |
| S09 | HARD-DEFER | hybrid GDN pad |
| S13 | HARD / BLOCKED | FLA / hybrid |
| S15 | skip | overlaps S14 — no FE writeup |
| S21 | HARD | Spec+DP dummy stale |
| S27 | BLOCKED | MLA pe pre-sliced |

These have capability rows (`未跑` / skip) but **no** WHY + **no** skills-run analysis package.

---

## Coverage cheatsheet

| Artifact | Coverage |
|----------|----------|
| Capability matrix row | **152 / 152** |
| Strong WHY (PASS/GAP/INVALID) | **~143 / 152** |
| Individual skills-run `Sxx-*.md` | **~134 / 152** (early gaps filled partly by batch wave) |
| Batch case-study credit | S01,S06–S08,S10′,S11–S12,S14,S16–S19 |
| Layers.json (root or nested) | most PASS/GAP; sparse on HARD |

---

## Gaps to close (docs only — no mining)

1. **S08:** add root `WHY_PASS.md` (+ optional `S08-20261018.md` skills-run) from existing PASS rates/evidence.  
2. **HARD list (9):** leave stub unless unparked; optionally one-liner “parked — no offline package” already in capability.  
3. **C:** no doc debt for completeness; do not expand.

---

## Verdict

**否 — 未全部完备。** 严格计：**142 完备 / 1 偏薄（S08） / 9 HARD·skip 缺失**。若只问「PASS+GAP 是否有 WHY+能力表」：几乎全有，唯 S08 缺正式 `WHY_PASS`。
