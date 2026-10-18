# Anomaly overlay principles / 异常场景原则

Guard pin: **G2** `f2aefd068`. Faults via **overlay only** (never edit canonical product trees).  
Canonical matrix: [`MATRIX.md`](./MATRIX.md). Positive controls: `synthetic/` (not in the 10-gate).

This document is the **binding protocol** for S01–S09 (and future scenarios). Amplified-only prior PASSes are **invalid** under these rules.

---

## 1. Origin-faithful / 忠于原 bug 逻辑

| EN | 中文 |
|----|------|
| Overlay must reproduce the **same logic** as the original bug (KV/cache corruption path, wrong condition, MoE routing bug, pad sentinel write-through, etc.). | Overlay 必须走与原 bug **同一逻辑路径**（KV/缓存脏读、错误条件、MoE 路由错、pad sentinel 写穿等）。 |
| **Amplified-only ≠ PASS.** Force-writing the symptom (NaN / repeated tokens) so a detector lights up does **not** count as a gate PASS. | **仅靠放大器 ≠ PASS。** 强行写入症状让 detector 亮灯，不算门禁通过。 |
| Tag each SPEC: `repro_mode: origin` \| `origin_tuned` \| `blocked` \| `hard_defer`. | 每个 SPEC 标注：`repro_mode: origin` \| `origin_tuned` \| `blocked` \| `hard_defer`。 |

---

## 2. Forbidden / 禁止

Do **not** invent the symptom:

- Force-write **NaN/Inf** into logits, scales, KV, or hidden states (e.g. wrap `compute_logits` NaN poison).
- **`fill_` / force repeated tokens** into sampler output (e.g. `sampled_token_ids.fill_(哈)`).
- Any other **synthetic amplifier** whose only job is to invent NaN / garbage / repeats so detectors fire.

`synthetic/` g_inject controls remain valid for **detector UT / positive control** — they are **not** 10-gate PASS evidence.

---

## 3. Allowed knobs / 允许调参（提高复现率，不改 bug 逻辑）

Use these to raise **trigger / precision / detect** rates without inventing the symptom:

| Knob | Notes |
|------|--------|
| KV / cache size | Smaller GPU util / tighter KV pool → more block churn, dirtier reuse |
| `max-model-len` / block size | Push slot / CP / pad edges that match the bug |
| Judgment thresholds | Detector or bug-edge conditions that match the original failure (not fake tensors) |
| Concurrency / load shape | `max-num-seqs`, burst vs single, chunked prefill |
| Many requests / long window | Prefer volume over amplifiers |
| Seeds / repeats | Fixed seed + many trials |
| Parallel topology | TP/PP/CP/DCP **only if** it is the same code path as the bug |
| `gpu_memory_utilization` | **Healthy boot only** — not to fake tensors |

Record **original rate → tuned rate** and the knobs used (never list NaN/`fill_` as knobs).

---

## 4. Per-bug analysis in SPEC / 每个 SPEC 必写

Every scenario `SPEC.md` must list:

1. **Trigger predicate** — when the bug path is entered (condition / call site).
2. **Allowed knobs** for this bug (subset of §3).
3. **Forbidden knobs** (at least: no force NaN / no token fill; plus any bug-specific bans).
4. **Origin tag** + upstream / Ascend fix PRs.
5. **`repro_mode`** and three-layer rates (see §5).

---

## 5. Three layers / 三层指标（勿合并）

Measure and report **separately**. Trigger ≠ precision ≠ detect.

| Layer | Meaning | How to count |
|-------|---------|--------------|
| **trigger** | Bug path entered / condition hit | Clear log line + counter when the overlay path fires (once per trigger event; include req id / step / block·KV sizes / condition values — avoid per-token spam) |
| **precision** | Abnormal output actually observed | Bad tokens, naturally appearing NaN/Inf, wrong vs clean baseline, dump corruption, etc. |
| **detect** | Guard detector / report / dump fired | `report_*.json` / configured detector |

Many requests and multiple triggers may be needed. Window up to ~30 min is OK for a **real** repro.

Rates table columns should look like: `triggers/N` · `precision/N` · `detect/N` + knobs + host.

---

## 6. Time budget / 时间预算

- Prefer **≤5–10 min** after ready, with **many requests**.
- Up to **~30 min** OK when the origin path is real but rare.
- Do not burn hours on one HARD scenario — see §7.

---

## 7. Prioritize easy; HARD/DEFER; collect more bugs / 先易后难

| Priority | Action |
|----------|--------|
| **Easy** | Origin path clear + safe knobs → implement, tune, land three-layer rates first |
| **In-progress** | Origin overlay exists; rates still low — keep tuning with §3 knobs only |
| **HARD / DEFER** | Especially hard without amplifiers (e.g. dual-node HCCN, rare GDN/DCP-only, no safe knobs) → mark `hard_defer` / `blocked`, **stop sinking time**, **do not** force NaN/fill |

Prefer filling toward ~10 scenarios by **collecting more candidate bugs** (recent vLLM / vllm-ascend precision PRs; prefer **`both` / `ascend-only`**) rather than forcing amplifiers on HARD ones.

---

## 8. FAIL rule / FAIL 判定

| Outcome | When |
|---------|------|
| **PASS** | Origin-faithful overlay + **detect** layer hit (detector/report/dump) within budget |
| **FAIL** | Overlay applied, boot OK, **precision** anomaly **actually reproduced**, but detector missed → save several raw abnormal outputs + `WHY_UNDETECTED.md` |
| **setup** | Boot / inject / config / model-op miss — anomaly never reproduced (not FAIL) |
| **BLOCKED** | Lab/env constraint (e.g. HCCN) — not a detector gap |

Boot/setup failures are **not** FAIL.

---

## 9. Origin tags / 来源标签

Every SPEC must mark exactly one:

| Tag | Meaning | Priority |
|-----|---------|----------|
| `both` | Shared failure mode / logic on upstream and Ascend | **P0 — prefer** |
| `ascend-only` | Ascend-specific path | **P0 — prefer** |
| `vllm-only` | Upstream-only path Ascend rewrites / does not share | P2 deferred (Ascend often bypasses) |

---

## 10. Env constraint — S04 PD / 环境约束

**S04** (P/D KV early reformat) prefers **same-host 1P1D** (two card groups + loopback metadata). Cross-host 160↔162 remains unavailable.  
Lab status: **HCCN device IPs not configured / links DOWN** — Ascend Mooncake **data plane** still needs HCCN even on one node → transfer boot may fail. Do not invent IPs. Complementary: **S21** dummy陪跑 (#56734, DP+spec, no Mooncake).

---

## Detector gaps (recorded, not implemented here)

See [`DETECTOR_GAPS.md`](./DETECTOR_GAPS.md). Notably **S01 / S07**: finite garbage / identical-across-requests — `logits_finite` misses → keep **FAIL+GAP**, do **not** amplify to PASS, do **not** land a garbled-text detector in overlay work.

## Quick checklist (authors)

- [ ] Overlay matches original bug logic (`repro_mode: origin` / `origin_tuned`)
- [ ] No NaN force-write / no token `fill_` amplifiers
- [ ] SPEC: trigger predicate + allowed/forbidden knobs + origin tag
- [ ] Trigger log + counter when bug path fires
- [ ] Rates: trigger / precision / detect reported separately
- [ ] FAIL only with real abnormal samples + `WHY_UNDETECTED`
- [ ] HARD ones deferred; collect more `both`/`ascend-only` bugs instead
- [ ] Detector misses recorded in `DETECTOR_GAPS.md` (FAIL+GAP ≠ PASS)
