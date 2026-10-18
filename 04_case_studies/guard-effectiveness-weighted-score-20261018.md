---
cursor:
  subagentId: "bc-fea3f65c-820d-58a1-a9ad-17d3943fe455"
---

# Guard 实际作用分 — typed / de-soft-inv-weighted (2026-10-18)

**Universe:** A∪B + GAP siblings（**排除 C** ones/zeros/abs matrix 刷分）。  
**Policy:** [`anomaly-mining-policy-pr-rooted-20261018.md`](./anomaly-mining-policy-pr-rooted-20261018.md) · **Eval:** [`guard-skills-evaluation-pr-weighted-20261018.md`](./guard-skills-evaluation-pr-weighted-20261018.md)

---

## 1. Scale definition（解决度 `r`）

Per-case degree（再按 type 取均值）：

| Score | Meaning |
|------:|---------|
| **0.00** | miss / FAIL+GAP（未检出） |
| **0.25** | detect-only **L1**（有 report，无稳定 class） |
| **0.60** | **L2** class-hint（现象类定界；本波主水平） |
| **0.85** | **L3** module-bound（verify + ref-kv 首分歧；本快照**未计**「L3 潜力」） |
| **1.00** | **L4** root-cause（算子行/commit；期望 ~0，本快照 **0**） |

**Notes**
- S23/S24 → **0.25**（L1）。
- S01/S07/S45 → **0.00**（GAP），计入对应 type 权重，诚实拉低 `d`/`r`。
- KV 场景能力表写「L2–L3 潜力 / 可选 L3」→ 本分仍按 **L2=0.60**（未系统刷满 L3）。
- C bucket **不入分母、不入分子**；附录仅列排除规模。

### Identity

对任意 type，若 miss/GAP 的 per-case `r=0`，则：

`r̄_t`（全员均值）= `d_t × r̄_t^(detected)`

因此：

**Guard 实际作用分** `S = Σ_t (w_t × d_t × r̄_t^(det)) = Σ_t (w_t × r̄_t)`

另报：
- **weighted detect** `D = Σ_t (w_t × d_t)`
- **weighted resolve** `R = Σ_t (w_t × r̄_t)` （与 `S` 同值，因上式）

**`S = 1.0` 含义：** 每个 type 按 A∪B+GAP 真实占比加权后，全部检出 **且** 全部达到 L4 根因定位。当前 skills 设计上限约 L2–L3 ⇒ 理论天花板约 **0.60–0.85**，不是 1.0。

---

## 2. Universe

| Set | n | 说明 |
|-----|---|------|
| **A∪B + GAP**（计分） | **34** | A PR-linked/real-class + B type keepers + S01/S07/S45 |
| C excluded | ~110 | soft-inv 刷分；不计入任何实际指标 |
| Naive full PASS detect（对照） | ~139/142 ≈ **97.9%** | 含 C，虚高 |

---

## 3. Per-type table（主权重 `w_t` on A∪B+GAP）

`w_t = n_t / 34` · `d_t = detect>0 / n_t` · `r̄_t` = mean per-case degree（含 GAP=0）· `r̄_t^(det)` = mean among detected only · 贡献 = `w_t × d_t × r̄_t^(det)`

| Type | n | w_t | d_t | r̄_t | r̄^(det) | **w×d×r** | IDs |
|------|---|-----|-----|------|---------|-----------|-----|
| KV·PD·pad | 7 | 0.206 (20.6%) | 0.857 (85.7%) | 0.514 | 0.600 | 0.1059 | S08, S11, S12, S30, S32, S10′, S01 |
| MoE | 5 | 0.147 (14.7%) | 1.000 (100.0%) | 0.600 | 0.600 | 0.0882 | S06, S16, S17, S18, S19 |
| RoPE·positions | 5 | 0.147 (14.7%) | 1.000 (100.0%) | 0.600 | 0.600 | 0.0882 | S25, S28, S40, S104, S105 |
| Embed·hidden·logits·sampler | 4 | 0.118 (11.8%) | 0.750 (75.0%) | 0.450 | 0.600 | 0.0529 | S10, S43, S46, S45 |
| Quant·weight | 4 | 0.118 (11.8%) | 0.750 (75.0%) | 0.275 | 0.367 | 0.0324 | S14, S23, S24, S07 |
| Overflow·softcap | 2 | 0.059 (5.9%) | 1.000 (100.0%) | 0.600 | 0.600 | 0.0353 | S20, S33 |
| Residual | 2 | 0.059 (5.9%) | 1.000 (100.0%) | 0.600 | 0.600 | 0.0353 | S31, S48 |
| Attn Q/K/V·out | 1 | 0.029 (2.9%) | 1.000 (100.0%) | 0.600 | 0.600 | 0.0176 | S47 |
| Other | 1 | 0.029 (2.9%) | 1.000 (100.0%) | 0.600 | 0.600 | 0.0176 | S49 |
| RMSNorm | 1 | 0.029 (2.9%) | 1.000 (100.0%) | 0.600 | 0.600 | 0.0176 | S26 |
| Spec | 1 | 0.029 (2.9%) | 1.000 (100.0%) | 0.600 | 0.600 | 0.0176 | S22 |
| SwiGLU | 1 | 0.029 (2.9%) | 1.000 (100.0%) | 0.600 | 0.600 | 0.0176 | S50 |
| **Σ** | **34** | **1.000** | — | — | — | **0.5265** | |

### Totals

| Metric | Value |
|--------|------:|
| **Guard 实际作用分 S** | **0.526** |
| Weighted detect D = Σ w·d | **0.912**（91.2%） |
| Weighted resolve R = Σ w·r̄ | **0.526**（= S） |

### Top type contributions（w×d×r）

KV·PD·pad 0.106, MoE 0.088, RoPE·positions 0.088, Embed·hidden·logits·sampler 0.053, Overflow·softcap 0.035

---

## 4. Second weight — A-only（PR-linked + GAP S01/S07）

`w_t^A = n_t / 20` among PR-linked/real-class attempts（n=20）。

| Type | n | w^A | d | r̄ | w×d×r |
|------|---|-----|---|-----|-------|
| KV·PD·pad | 6 | 0.300 | 0.833 | 0.500 | 0.1500 |
| MoE | 4 | 0.200 | 1.000 | 0.600 | 0.1200 |
| RoPE·positions | 4 | 0.200 | 1.000 | 0.600 | 0.1200 |
| Quant·weight | 2 | 0.100 | 0.500 | 0.300 | 0.0300 |
| Embed·hidden·logits·sampler | 1 | 0.050 | 1.000 | 0.600 | 0.0300 |
| Overflow·softcap | 1 | 0.050 | 1.000 | 0.600 | 0.0300 |
| RMSNorm | 1 | 0.050 | 1.000 | 0.600 | 0.0300 |
| Spec | 1 | 0.050 | 1.000 | 0.600 | 0.0300 |
| **Σ** | **20** | 1 | — | — | **0.5400** |

A-only Guard 分 ≈ **0.540**；weighted detect ≈ **0.900**。与主分接近（略偏 KV/MoE/RoPE）。

---

## 5. Interpretation

| 读法 | 结论 |
|------|------|
| **S ≈ 0.53** | 去掉刷分后，按真实 type 占比加权，Guard+skills 约在「**高检出 × L2 定界**」水平，远未到根因 |
| vs naive **~98% detect** | 虚高：C 占 PASS ~78%，且把「检出」当成「解决」 |
| vs weighted detect **91.2%** | 更诚实的检出；仍偏高，因 A∪B 多为已 PASS 的可触发算子故障 |
| Gap drag | S01/S07/S45 拉低 KV / Quant / Embed 的 d 与 r |
| Ceiling | 无 L4 ⇒ 即使 100% detect+L2，S 上限 ≈ **0.60**；本分 0.53 ≈ 该上限的 **88%** |

**一句话：** Guard 实际作用分 **0.53 / 1.0**（L2 天花板 ~0.60 时相当于 **88%** 发挥）；主要贡献来自 **KV·PD、MoE、RoPE**；短板是 **garbled-GAP** 与 **Quant L1**。

---

## 6. Appendix — excluded C（不计入）

C ≈ **110** PASS soft-inv 冗余（ones/zeros/abs/mag/polarity matrix）。  
若误把 C 算进 detect 头条 → S25+ ≈ 100%、全量 ≈ 98%。**本文件全部实际指标已排除 C。**

---

## 7. Repro formula (copy-paste)

```
for each type t in A∪B∪GAP:
  w_t = n_t / N
  d_t = (# detect>0) / n_t
  r_i ∈ {0, 0.25, 0.6, 0.85, 1.0}
  r̄_t = mean_i r_i          # GAP/miss → 0
  contrib_t = w_t * r̄_t     # == w_t * d_t * mean(r | detected)
S = sum contrib_t
```
