---
cursor:
  subagentId: "bc-fea3f65c-820d-58a1-a9ad-17d3943fe455"
---

# Docs 典型模版用例 keep-set（2026-10-19）

**目的：** 公开 `04_case_studies/` 只留高教学价值案例；其余 soft-inv 重复与近邻 L2 迁到 `runtime-guard-test`（runs / fail-evidence）。  
**范围：** 优先 **A∪B+GAP**；**C 几乎全部迁出**。  
**状态：** 已落地 — 公开 `examples/` 15 模版；大体积分析全文在 `runtime-guard-test/docs/`（本仓 stub）。  
**相关：** [`case-studies-runs-archive-proposal-20261019.md`](./case-studies-runs-archive-proposal-20261019.md)

---

## 0. 选型原则（按实际情况，非 1-type-1-case）

1. **差异化课**：GAP / L1-only / 独特 detector / 不同 root-cause / 不同症状 — 才保留。  
2. **同 type 可 >1**：仅当课不同（如同族 PASS vs GAP，或 pad vs recycle）。  
3. **同 type 近邻 L2 / ones·zeros·abs 矩阵（C）**：迁出。  
4. **MoE 饱和**：公开模板最多 1 个。  
5. **HARD 未跑**：不进「典型模版」（能力表 stub 即可）。

---

## 1. Recommended keep list（**N = 15**）

| ID | Type | 为何留（一句话） |
|----|------|------------------|
| **S01** | KV·PD·pad | **GAP**：KV skip-zero → 有限混合垃圾；教 `logits_finite` 缺口 |
| **S10′** | KV·PD·pad | **同族 PASS**（FullAttn recycle-zero）；与 S01 对照「能检 vs 漏检」 |
| **S11** | KV·PD·pad | MLA **pad-tail**；与 recycle 不同 root-cause（第二课） |
| **S07** | Quant·weight | **GAP**：W8A8 scale collapse；与 S01 同缺口、不同根因 |
| **S23** | Quant·weight | **L1-only**：权重置零 always-on；能检不能定界到元素 |
| **S45** | Embed·logits·sampler | **GAP**：`-logits` top-k → unique garbage（第三种漏检形态） |
| **S43** | Embed·logits·sampler | **PASS** embed×100 / newline collapse；与 S45 对照 |
| **S22** | Spec | 独特 **`spec_acceptance`** 分布性课（#18657） |
| **S06** | MoE | MoE 路由最简 L2；饱和类**只留这 1 个** |
| **S26** | RMSNorm | **PR-rooted** soft-inv 样板（#42379） |
| **S25** | RoPE·positions | **PR-rooted** RoPE soft-inv 样板（#7082 half-drop） |
| **S50** | SwiGLU | SwiGLU 算子 L2 代表（half-swap） |
| **S48** | Residual | Residual 极性 → `logits_finite` / `!!!!` |
| **S47** | Attn Q/K/V·out | Attn 算子 L2 代表 |
| **S33** | Overflow·softcap | overflow / bang 塌缩代表 |

### Optional lean cut（若想更短 → **N = 11**）

去掉仍有近邻课的：**S11**（KV 只留 S01+S10′）、**S43**（Embed 只留 GAP S45）、**S47**、**S33**（算子课用能力表一行带过）。  
**主推荐仍为 15**（对公开读者课覆盖更完整）。

---

## 2. Count by type

| Type | Keep n | IDs |
|------|-------:|-----|
| KV·PD·pad | 3 | S01, S10′, S11 |
| Quant·weight | 2 | S07, S23 |
| Embed·hidden·logits·sampler | 2 | S45, S43 |
| Spec | 1 | S22 |
| MoE | 1 | S06 |
| RMSNorm | 1 | S26 |
| RoPE·positions | 1 | S25 |
| SwiGLU | 1 | S50 |
| Residual | 1 | S48 |
| Attn Q/K/V·out | 1 | S47 |
| Overflow·softcap | 1 | S33 |
| **Σ** | **15** | — |

未单独占坑的 type：**Other**（S49 教学价值低）。HARD（S02–S05…）不进 keep。

---

## 3. Move list summary（docs 不留模版 / 不放满量 runs）

| Bucket | ~Count | 处理 |
|--------|-------:|------|
| **C soft-inv 刷分** | **~110** | **几乎全部迁出**；命名模式：`S5x–S152` 上 ones/zeros/abs/×÷/极性矩阵及同类 L2 近邻 |
| **A∪B 未入 keep** | **18** | 迁出公开模版（证据仍留 test）：S08, S12, S14, S16–S20, S24, S28, S30–S32, S40, S46, S49, S104, S105 等 |
| **整目录 `anomaly-skills-runs/`** | **135** | 按前序提案迁出 docs → test `docs/anomaly-skills-runs/`；keep 的 15 个可各写 **1 页短模版** 链到 test |
| **HARD / skip stubs** | **9** | 不进典型模版（能力表已有） |

C 名称模式（示例）：`*ones*` / `*zeros*` / `*abs*` / `*_scale_*` / `*_negate*` 及同算子大量 mag/polarity 变体（见 mining policy inventory）。

---

## 4. Final number

> **docs 典型 case ≈ 15**（主推荐）  
> 可选精简 ≈ **11**  
> 公开 `04` 另保留分析/政策 md（capability、eval、score、policy…），**不**再堆 134 条 run stub。

---

## 5. 落地状态

- 每 keep ID：`04_case_studies/examples/Sxx_<short>.md`（或扁平 `case-Sxx.md`）≈20–40 行 + 链到  
  `runtime-guard-test/docs/anomaly-skills-runs/` 与 `tests/build-anomaly-env/fail-evidence/Sxx/`。  
- README 索引改为「15 典型 + 分析文档」；删除/停 sync docs 侧满量 runs。  
- **Do not move in this turn** — 仅清单。
