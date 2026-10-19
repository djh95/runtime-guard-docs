---
cursor:
  subagentId: "bc-fea3f65c-820d-58a1-a9ad-17d3943fe455"
---

# Proposal: move `anomaly-skills-runs/` out of public docs (2026-10-19)

**Suggestion:** Move `04_case_studies/anomaly-skills-runs/` (S01–S152 skill run traces) out of public `runtime-guard-docs` into `runtime-guard-test` evidence; keep in `04` only typical template cases + analysis docs.

**Status:** analysis only — **no files moved**.

---

## 1. Verdict — is it reasonable?

**Yes — reasonable.** Runs are tiny, repetitive, auto-generated verify traces; they bloat the public case-studies index without teaching the product narrative. Canonical evidence already lives better next to skills + fail-evidence in the test repo.

| Pros | Cons |
|------|------|
| Public `04` stays readable (analysis/policy, not 134 micro-logs) | External readers lose one-click browse of every Sxx run in docs |
| Matches ownership: skills verify ↔ `runtime-guard-test` | Need README pointers so docs don’t look “empty” |
| Shrinks docs clone noise (~46KB / 135 files — small bytes, high file count) | Dual-push workflows that copy runs → docs must stop |
| Test repo **already has** the same tree | Brief link churn in capability / eval docs that cite `anomaly-skills-runs/Sxx-…` |

**Not a size crisis** (whole `04` ≈ 247KB; runs ≈ 46KB / 19%). The win is **signal/noise and repo role**, not disk.

---

## 2. Inventory — `04_case_studies/` top-level

| Kind | Count | Notes |
|------|------:|-------|
| Top-level **files** | **13** | README + analysis/policy/eval/status |
| Top-level **dirs** | **1** | `anomaly-skills-runs/` only |
| **Total under `04`** | ≈ **247 KB** | |

Largest files (approx):

| File | ~Size | Role |
|------|------:|------|
| `anomaly-skills-capability-20261017.md` | 89 KB | Living capability matrix |
| `anomaly-skills-verify-loop-20261017.md` | 45 KB | before→after verify log |
| `anomaly-mining-policy-pr-rooted-20261018.md` | 17 KB | Mining policy + inventory |
| `guard-skills-evaluation-*.md` (+ PR-weighted) | 6–13 KB | Eval narratives |
| `guard-effectiveness-weighted-score-20261018.md` | 6 KB | Typed Guard score |
| Others (PRINCIPLES, audit, handoff, status, wave note) | &lt;8 KB each | Ops / protocol |

---

## 3. Inside `anomaly-skills-runs/`

| Metric | Value |
|--------|------:|
| Files | **135** (134× `Sxx-20261017.md` + 1× `batch-pass-wave-20261017.md`) |
| Total size | ≈ **46 KB** |
| Avg / median | ≈ **343 B** / **300 B** |
| Range | 247–1346 B |

**Nature:** short offline skills-verify stubs — evidence path, three-layer rates, detector hit, L1/L2 bound, ≠ neighbors. Not full case studies; mostly **auto/semi-auto traces** from the 162 skills loop. Duplicate already under test-repo `docs/anomaly-skills-runs/` (135 files).

---

## 4. After moving runs away — what remains in `04_case_studies/`?

**~13 markdown files + README** (no bulky dir). By category:

### A. Analysis / eval / policy（主留存）

| Doc | Purpose |
|-----|---------|
| `anomaly-skills-capability-20261017.md` | Per-scenario detect/L-bound matrix |
| `anomaly-skills-verify-loop-20261017.md` | Skills edit → re-verify history |
| `anomaly-skills-analysis-20261017.md` | Wave analysis notes |
| `guard-skills-evaluation-20261017.md` | Raw full-corpus eval appendix |
| `guard-skills-evaluation-pr-weighted-20261018.md` | PR-weighted eval (headline) |
| `guard-effectiveness-weighted-score-20261018.md` | Typed Guard score S≈0.53 |
| `anomaly-mining-policy-pr-rooted-20261018.md` | PR-rooted mining + typed inventory |
| `anomaly-analysis-docs-audit-20261018.md` | Doc completeness audit |
| `anomaly-PRINCIPLES.md` | Origin-faithful overlay protocol |

### B. Per-scenario case writeups

| Status | Notes |
|--------|-------|
| **None as standalone “故事”文章** | Individual Sxx prose today **is** the runs dir (+ capability rows). After move: **0** per-scenario writeups in public `04` unless you add ~few template cases (see §5). |

### C. Templates

| Doc | Purpose |
|-----|---------|
| `README.md` | Writing template for future human case studies + index (A1–A10) |

### D. Other / ops status

| Doc | Purpose |
|-----|---------|
| `anomaly-skills-handoff.md` | 160↔skills inbox / poll |
| `anomaly-repro-status-20261016.md` | Repro status snapshot |
| `anomaly-s29-s31-older-pr-wave2-20261017.md` | Small wave note |

---

## 5. Recommend — keep ~few 典型模版用例 in docs

Keep **5 short example pages** (or one `examples/` folder with 5 files) that teach **distinct product lessons**, each linking to test-repo evidence/runs for depth:

| Keep as public example | Why typical |
|------------------------|-------------|
| **S01** (GAP garbled) | Detector miss / finite junk — CANNOT story |
| **S06** or **S16** (MoE) | Classic L2 class-hint PASS |
| **S11** or **S12** (KV·PD) | KV family + L3 potential |
| **S22** (Spec) | Non-text detector (`spec_acceptance`) |
| **S26** (RMSNorm PR-linked) | One-PR→one-class soft-inv done right |

Optional 6th: **S23** (Quant L1 detect-only) to show ceiling.  
**Do not** keep C-matrix ones/zeros clones as public templates.

Body of each example: 20–40 lines (symptom / layers / detector / skills bound / link to `runtime-guard-test` paths). Rest of Sxx → test evidence only.

---

## 6. Exact target path (test repo)

**Recommended canonical:**  
`runtime-guard-test/docs/anomaly-skills-runs/`  
(already present; same 135 files — **delete docs-repo copy**, don’t duplicate into fail-evidence)

| Path | Role |
|------|------|
| `docs/anomaly-skills-runs/` | **Canonical** skills-verify traces |
| `tests/build-anomaly-env/fail-evidence/Sxx/` | Raw WHY/layers/samples (heavier) — runs should **point here**, not live inside |
| `04_case_studies/` (docs) | Analysis + ~5 template examples + README links to test paths |

**Migration sketch (when approved):** remove `runtime-guard-docs/04_case_studies/anomaly-skills-runs/`; update README A5 → “see test-repo `docs/anomaly-skills-runs/`”; add `examples/` or inline 5 templates; stop dual-push of run stubs to docs main.

---

## 7. Numbers summary

| Item | Count |
|------|------:|
| `04` top-level files today | 13 |
| `04` top-level dirs today | 1 (`anomaly-skills-runs`) |
| Run traces | 135 (~46 KB) |
| After move, public `04` content | **13 analysis/ops md** (+ optional **~5** new template examples) |
| Per-scenario writeups left in docs without templates | **0** |
