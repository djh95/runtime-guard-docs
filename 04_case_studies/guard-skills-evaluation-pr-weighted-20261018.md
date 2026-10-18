---
cursor:
  subagentId: "bc-fea3f65c-820d-58a1-a9ad-17d3943fe455"
---

# Runtime Guard × Skills — PR-weighted evaluation (2026-10-18)

**Supersedes headline metrics in** [`guard-skills-evaluation-20261017.md`](./guard-skills-evaluation-20261017.md) (raw appendix retained there / below).  
**Mining policy:** [`anomaly-mining-policy-pr-rooted-20261018.md`](./anomaly-mining-policy-pr-rooted-20261018.md)  
**Scope:** S01–S152; skills v5.8; Guard pin G2. **No new 160 mining** in this refresh.

---

## 0. Why rewrite

Previous headline (~**99–100%** detect on S25+ / PASS corpus) was **inflated by soft-inv density**:

| Corpus slice | n | Share of PASS |
|--------------|---|----------------|
| **C** soft-inv redundancy (ones/zeros/abs/mag matrix) | **110** | **78.0%** |
| **A** PR-linked real-class | **18** | **12.8%** |
| **B** non-redundant type representatives | **13** | **9.2%** |

**C must not count toward “Guard strength” headlines.** Primary verdict uses **A∪B** (and GAP siblings where the class was attempted).

---

## 1. Headline metrics (corrected)

### 1.1 Primary — PR-weighted / de-duplicated (A∪B)

| Metric | Value | Notes |
|--------|-------|-------|
| **Set size** | **31** | A=18 + B=13 (excl. C=110) |
| **Detect>0** | **31/31 ≈ 100%** among A∪B PASSes | Still strong on runnable operator/PR classes that already PASSed |
| **Detect incl. GAP siblings** | **31/34 = 91.2%** | Denominator + **S01/S07/S45** (same families attempted, detect miss) |
| **L2 class-hint** | **~29/31 ≈ 93.5%** | S23/S24 stay **L1 detect-only** (weight/quant) |
| **L4 root-cause** | **0** | Unchanged — skills do not claim commit/op-line |

> **Reading:** Soft-inv 刷分 made “S25+ = 100% detect” look like general competence. On the de-duplicated set, online detect remains high for **collapse/repeat / nonfinite** classes, but **~9%** of the PR-weighted attempted numeric classes are still **GAP (garbled)**.

### 1.2 Transparent — full corpus (includes C)

| Metric | Value |
|--------|-------|
| Capability “能否检测=是” | **139 / 152 ≈ 91.4%** (incl. HARD/未跑 in denom) |
| Attempted with outcome (PASS+GAP) | **139 / 142 ≈ 97.9%** detect (3 GAP) |
| S25+ PASS (old headline) | **126 / 126 = 100%** — **of which ~87% are C**; **do not cite as Guard strength** |
| L2 on capability PASS rows | **~140 / 152** table marks (inflated by C) |

### 1.3 Inflation callout

| Old claim | Corrected |
|-----------|-----------|
| S25+ detect **100%** ⇒ Guard “solved” soft-inv wave | S25+ majority is **C**; primary A∪B is **31** scenarios; with GAP → **91.2%** |
| ~98–99% detect on runnable PASS | Transparent OK to report, but **not** the product verdict |

---

## 2. Type proportions (actual mix)

### 2.1 PASS inventory by type (N=141)

| Type | n | % PASS | A | B | C |
|------|---|--------|---|---|---|
| RMSNorm | 21 | 14.9% | 1 | 0 | 20 |
| SwiGLU | 21 | 14.9% | 0 | 1 | 20 |
| Embed·hidden·logits·sampler | 18 | 12.8% | 1 | 2 | 15 |
| RoPE·positions | 18 | 12.8% | 4 | 1 | 13 |
| Attn Q/K/V·out | 17 | 12.1% | 0 | 1 | 16 |
| Residual | 17 | 12.1% | 0 | 2 | 15 |
| KV·PD·pad | 9 | 6.4% | 5 | 1 | 3 |
| Overflow·softcap | 7 | 5.0% | 1 | 1 | 5 |
| Quant·weight | 6 | 4.3% | 1 | 2 | 3 |
| MoE | 5 | 3.5% | 4 | 1 | 0 |
| Other | 1 | 0.7% | 0 | 1 | 0 |
| Spec | 1 | 0.7% | 1 | 0 | 0 |

**Observation:** RMSNorm + SwiGLU + Residual + Attn + RoPE + Embed ≈ **79%** of PASS — heavily soft-inv-padded. MoE/Spec/Quant/KV are small but over-represented in **A**.

### 2.2 Non-PASS / parked (not in % above)

| Bucket | IDs |
|--------|-----|
| **garbled-GAP** | S01, S07, S45 |
| **HARD / BLOCKED / DROPPED** | S02, S03, S04, S05, S09, S13, S21, S27 |
| **INVALID** | S44 |

---

## 3. Detection detail (grounded in type mix)

### 3.1 What still works (CAN) — on A∪B

| Family | Keepers / PR-linked | Typical detector | Skills |
|--------|---------------------|------------------|--------|
| KV·PD·pad | S08, S10′, S11, S12, S30 | `token_repeat` (+L3 potential) | L2 |
| MoE | S06, S16, S17 (+S18/S19 A but mining-redundant) | `token_repeat` | L2 |
| RMSNorm | S26 (#42379) | `token_repeat` | L2 |
| RoPE | S40 (+ PR soft-inv S25/S28 under A) | `token_repeat` | L2 |
| Spec | S22 (#18657) | `spec_acceptance` | L2 |
| Quant/weight | S23, S24 | detect-only | **L1** |
| SwiGLU / Residual / Attn / Embed / Overflow | S50, S31/S48, S47, S43/S46, S33 | repeat / finite | L2 |

Common trait: **single triggerable tensor fault** → repeat collapse or nonfinite logits.

### 3.2 What fails (CANNOT) — unchanged priorities

| Gap | IDs | Why |
|-----|-----|-----|
| **Garbled / unique / mixed-script finite junk** | S01, S07, S45 | `token_repeat` + `logits_finite` miss |
| **L4 root-cause** | all | out of skills scope |
| **Weight element localization** | S23/S24 | L1 only |
| **HARD subsystems** | graph/CP/PD/Spec+DP/hybrid | infra / weights — mark HARD, no soft-inv credit |

**Optimization priority #1:** garbled-text / cross-request-identical / unique-garbage **detector** (not more C overlays).

---

## 4. Localization

| Level | Full corpus (incl. C) | A∪B primary |
|-------|----------------------|-------------|
| L1 | S23/S24 + noise | **2** (S23/S24) |
| L2 | ~140 | **~29** |
| L3 | rare / potential on KV | same potential (S10′/S12/S30) |
| L4 | 0 | 0 |

≠ differentiation inside C was mostly “≠ adjacent mag/zeros/ones” — **low product value**; A∪B ≠ lines should cite **PR / class**, not matrix neighbors.

---

## 5. Overall verdict (PR-weighted)

**Guard + skills are strong on a small, typed set of origin-faithful / representative numeric faults (detect≈100% on A∪B PASSes; ≈91% if GAP counted), and weak on garbled finite text + unrun HARD subsystems.**

They are **not** proven at the old ~98–100% “wave” rate once soft-inv 刷分 is removed from the denominator of merit.

---

## 6. Raw appendix pointers

- Prior narrative eval (pre–PR-weight): [`guard-skills-evaluation-20261017.md`](./guard-skills-evaluation-20261017.md)
- Capability table: [`anomaly-skills-capability-20261017.md`](./anomaly-skills-capability-20261017.md)
- Inventory + caps: [`anomaly-mining-policy-pr-rooted-20261018.md`](./anomaly-mining-policy-pr-rooted-20261018.md) §§3–4
- Fail evidence: `anomaly-fail-evidence/`
