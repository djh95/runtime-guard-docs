# Runtime Guard × Skills 评估（2026-10-18，去刷分 PR-weighted + 作用分）

**范围：** origin-faithful anomaly 环境 S01–S152；skills v5.8；Guard pin G2（`f2aefd068`）。
**协议约束：** 不计 force-NaN / `fill_` / `logits.zero_()` 等 amplifier；S44 INVALID 非 skills 胜利；S23/S24 权重·量化 always-on 仅 detect-only（L1）。

> 本文是 10-18 一次评估工作的**定性 + 量化合并版**，取代此前三份：
> `guard-skills-evaluation-20261017.md`（raw 全量附录）、`guard-skills-evaluation-pr-weighted-20261018.md`、`guard-effectiveness-weighted-score-20261018.md`。
> Mining 政策全文在内部仓 `runtime-guard-test/docs/anomaly-mining-policy-pr-rooted-20261018.md`（需权限）。

---

## 0. 为什么重写（去刷分动机）

旧头条（S25+ / PASS 语料上「~99–100% detect」）被 **soft-inv 密度**抬高：

| Corpus 切片 | n | 占 PASS 比 |
|-------------|---|-----------|
| **C** soft-inv 冗余（ones/zeros/abs/mag/polarity 矩阵） | **110** | **78.0%** |
| **A** PR-linked 真实类 | **18** | **12.8%** |
| **B** 非冗余 type 代表 | **13** | **9.2%** |

**C 不计入「Guard 实力」头条。** 头条口径用 **A∪B**（同类故障被尝试时再并入 GAP 兄弟场景）。

---

## 1. 头条指标（修正后）

### 1.1 主口径 — PR-weighted / 去重（A∪B）

| 指标 | 值 | 说明 |
|------|----|------|
| 集合规模 | **31** | A=18 + B=13（排除 C=110） |
| Detect>0 | **31/31 ≈ 100%** | 对已 PASS 的可跑算子/PR 类 |
| Detect 含 GAP 兄弟 | **31/34 = 91.2%** | 分母加 **S01/S07/S45**（同类被尝试但漏检） |
| L2 class-hint | **~29/31 ≈ 93.5%** | S23/S24 停在 **L1 detect-only** |
| L4 root-cause | **0** | 不变 —— skills 不承诺 commit/算子行 |

> **读法：** soft-inv 刷分让「S25+ = 100%」显得像普适能力；去重后，在线检出在**塌缩/复读、非有限 logits** 类上仍高，但 ~9% 的 PR-weighted 已尝试数值类仍是 **GAP（有限垃圾）**。

### 1.2 透明口径 — 全量（含 C）

| 指标 | 值 |
|------|----|
| 能力表「能否检测 = 是」 | **139 / 152 ≈ 91.4%**（含 HARD/未跑分母） |
| 已尝试（PASS+GAP） | **139 / 142 ≈ 97.9%** detect（3 GAP） |
| S25+ PASS（旧头条） | **126 / 126 = 100%** —— **其中 ~87% 是 C**，勿当 Guard 实力引 |
| 能力表 L2 标注 | **~140 / 152**（被 C 抬高） |

### 1.3 虚高对照

| 旧说法 | 修正 |
|--------|------|
| S25+ detect 100% ⇒ Guard「解决」soft-inv 波 | S25+ 大多是 C；主口径 A∪B 仅 **31** 场景，含 GAP → **91.2%** |
| 可跑 PASS ~98–99% detect | 可作为透明口径报告，但**不是**产品结论 |

---

## 2. Type 构成（实际混合）

### 2.1 PASS 库存按 type（N=141）

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

RMSNorm + SwiGLU + Residual + Attn + RoPE + Embed ≈ **79%**，被 soft-inv 重度填充；MoE/Spec/Quant/KV 规模小但在 **A** 中占比高。

### 2.2 非 PASS / 停泊（不计入上述 %）

| 桶 | IDs |
|----|-----|
| **garbled-GAP** | S01, S07, S45 |
| **HARD / BLOCKED / DROPPED** | S02, S03, S04, S05, S09, S13, S21, S27 |
| **INVALID** | S44 |

---

## 3. 检测细节（基于 type 混合）

### 3.1 仍有效（CAN）— A∪B

| 家族 | Keepers / PR-linked | 典型 detector | Skills |
|------|---------------------|---------------|--------|
| KV·PD·pad | S08, S10′, S11, S12, S30 | `token_repeat`（+L3 潜力） | L2 |
| MoE | S06, S16, S17（S18/S19 为 A 但挖矿冗余） | `token_repeat` | L2 |
| RMSNorm | S26 (#42379) | `token_repeat` | L2 |
| RoPE | S40（+ PR soft-inv S25/S28 归 A） | `token_repeat` | L2 |
| Spec | S22 (#18657) | `spec_acceptance` | L2 |
| Quant/weight | S23, S24 | detect-only | **L1** |
| SwiGLU / Residual / Attn / Embed / Overflow | S50, S31/S48, S47, S43/S46, S33 | repeat / finite | L2 |

共同特征：**单一、可触发、可复现的张量故障** → 复读塌缩或非有限 logits。

### 3.2 失败（CANNOT）— 优先级不变

| 缺口 | IDs | 原因 |
|------|-----|------|
| **Garbled / unique / mixed-script 有限垃圾** | S01, S07, S45 | `token_repeat` + `logits_finite` 双漏 |
| **L4 根因** | 全部 | 超出 skills 范围 |
| **权重元素定位** | S23/S24 | 仅 L1 |
| **HARD 子系统** | graph/CP/PD/Spec+DP/hybrid | 基础设施 / 权重，标记 HARD，不给 soft-inv 记功 |

**优先级 #1：garbled-text / cross-request-identical / unique-garbage detector（不是更多 C overlay）。**

### 3.3 detector 分布（PASS 主检出，估计）

| Detector / 症状类 | PASS 场景数 | 说明 |
|-------------------|-------------|------|
| `token_repeat` | ~104 | 短语/digit/`!!!!`/复读塌缩 |
| `logits_finite` | ~24 | 非有限 logits / `!!!!`，常伴 residual/SwiGLU/norm 极性或爆幅 |
| `spec_acceptance` | 1（S22） | 分布性；samples 可「空标签」仍 L2 |

### 3.4 precision=0 但 detect>0（仍算 PASS）

契约：**precision=0 且 detect>0 ⇒ PASS，不是 GAP**。identical-mode / unique-mode 会低估「肉眼异常」，但 online detector 仍开火；已知 ≥9 处 metadata 显式 `precision=0 OK`（S92, S96, S98, S99, S103, S109, S113, S121, S124 等）。**三层率必须拆开读，先看 detect。**

---

## 4. 定位 / 定界

| 层级 | 全量（含 C） | A∪B 主口径 |
|------|-------------|------------|
| L1 detect-only | S23/S24 + 噪声 | **2**（S23/S24） |
| L2 class-hint | ~140 | **~29** |
| L3 module-bound | 少见 / KV 潜力 | 同潜力（S10′/S12/S30） |
| L4 root-cause | 0 | 0 |

- 能力表 `locate` 列几乎全「否」（~142 否 + 未跑「—」），与设计一致：skills 定界**停在现象类**，不到根因。
- C 内的「≠ 相邻 mag/zeros/ones」区分力**产品价值低**；A∪B 的「≠」应引用 **PR / class**，而不是矩阵邻居。

---

## 5. Guard 实际作用分（typed / 去 soft-inv 加权）

**Universe：A∪B + GAP 兄弟（合计 34，排除 C）。**

### 5.1 解决度 `r`

| Score | 含义 |
|------:|------|
| **0.00** | miss / FAIL+GAP（未检出） |
| **0.25** | detect-only L1 |
| **0.60** | L2 class-hint（本波主水平） |
| **0.85** | L3 module-bound（本快照未计「L3 潜力」） |
| **1.00** | L4 root-cause（期望 ~0，本快照 0） |

S23/S24 → 0.25；S01/S07/S45 → 0.00（GAP）；KV 类按 L2=0.60（未系统刷满 L3）；C 不入分母分子。

`Guard 实际作用分 S = Σ_t (w_t × d_t × r̄_t^(det)) = Σ_t (w_t × r̄_t)`，另报 weighted detect `D = Σ_t (w_t × d_t)`。`S=1.0` 表示每 type 全检出且全到 L4；skills 设计上限约 L2–L3 ⇒ 理论天花板 **0.60–0.85**。

### 5.2 Per-type 主表（`w_t = n_t / 34`）

| Type | n | w_t | d_t | r̄_t | r̄^(det) | w×d×r | IDs |
|------|---|-----|-----|------|---------|-------|-----|
| KV·PD·pad | 7 | 0.206 | 0.857 | 0.514 | 0.600 | 0.1059 | S08, S11, S12, S30, S32, S10′, S01 |
| MoE | 5 | 0.147 | 1.000 | 0.600 | 0.600 | 0.0882 | S06, S16, S17, S18, S19 |
| RoPE·positions | 5 | 0.147 | 1.000 | 0.600 | 0.600 | 0.0882 | S25, S28, S40, S104, S105 |
| Embed·hidden·logits·sampler | 4 | 0.118 | 0.750 | 0.450 | 0.600 | 0.0529 | S10, S43, S46, S45 |
| Quant·weight | 4 | 0.118 | 0.750 | 0.275 | 0.367 | 0.0324 | S14, S23, S24, S07 |
| Overflow·softcap | 2 | 0.059 | 1.000 | 0.600 | 0.600 | 0.0353 | S20, S33 |
| Residual | 2 | 0.059 | 1.000 | 0.600 | 0.600 | 0.0353 | S31, S48 |
| Attn Q/K/V·out | 1 | 0.029 | 1.000 | 0.600 | 0.600 | 0.0176 | S47 |
| Other | 1 | 0.029 | 1.000 | 0.600 | 0.600 | 0.0176 | S49 |
| RMSNorm | 1 | 0.029 | 1.000 | 0.600 | 0.600 | 0.0176 | S26 |
| Spec | 1 | 0.029 | 1.000 | 0.600 | 0.600 | 0.0176 | S22 |
| SwiGLU | 1 | 0.029 | 1.000 | 0.600 | 0.600 | 0.0176 | S50 |
| **Σ** | **34** | **1.000** | — | — | — | **0.5265** | |

| Metric | Value |
|--------|------:|
| **Guard 实际作用分 S** | **0.526** |
| Weighted detect D = Σ w·d | **0.912**（91.2%） |
| Weighted resolve R = Σ w·r̄ | **0.526**（= S） |

Top 贡献：KV·PD·pad 0.106、MoE 0.088、RoPE·positions 0.088、Embed·hidden·logits·sampler 0.053、Overflow·softcap 0.035。

### 5.3 第二权重 — A-only（PR-linked + GAP S01/S07，n=20）

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

A-only 分 ≈ **0.540**，weighted detect ≈ 0.900；与主分接近（略偏 KV/MoE/RoPE）。

---

## 6. 作用分解读

| 读法 | 结论 |
|------|------|
| **S ≈ 0.53** | 去刷分后按真实 type 占比加权，Guard+skills 约在「高检出 × L2 定界」水平，远未到根因 |
| vs naive ~98% detect | 虚高：C 占 PASS ~78%，且把「检出」当「解决」 |
| vs weighted detect 91.2% | 更诚实的检出；仍偏高，因 A∪B 多为已 PASS 的可触发算子故障 |
| Gap drag | S01/S07/S45 拉低 KV / Quant / Embed 的 d 与 r |
| 天花板 | 无 L4 ⇒ 即便 100% detect+L2，S 上限 ≈ 0.60；0.53 ≈ 该上限的 88% |

**一句话：** Guard 实际作用分 **0.53 / 1.0**（L2 天花板 ~0.60 时相当于 **88%** 发挥）；主要贡献来自 **KV·PD、MoE、RoPE**；短板是 **garbled-GAP** 与 **Quant L1**。

---

## 7. 能解决的家族（CAN，L2 为主）

| 家族 | 代表场景 | 典型 detector | skills 到达 |
|------|----------|---------------|-------------|
| RMSNorm | S26, S38, S66, S70–S74, S86–S89, S96, S145, S150… | repeat / finite | L2 |
| Residual | S31, S48, S55, S64, S88–S91, S93–S94… | 同上 | L2 |
| SwiGLU | S39, S50, S56, S67, S72, S76, S81… | 同上 | L2 |
| Attn Q/K/V·out | S34–S35, S41, S47, S49, S51–S54… | 多 `token_repeat` | L2 |
| RoPE·positions | S25, S28, S37, S40, S42, S57… | `token_repeat` | L2 |
| Embed·hidden·logits·sampler | S36, S43, S46, S53, S61, S65… | `token_repeat` | L2 |
| Overflow·softcap·bang | S20, S33, S38 | repeat / finite | L2 |
| MoE 路由 | S06, S16–S19 | `token_repeat` | L2 |
| Spec resample/SALT | S22 | `spec_acceptance` | L2 |
| KV/slot/pad/MLA（部分） | S08, S10′, S11, S12, S14, S30, S32 | `token_repeat`（+可选 L3） | L2（L3 潜力） |

---

## 8. 优化空间（按优先级）

1. **新 detector：garbled / mixed-script / unique-garbage / identical-across** —— 解锁 S01/S07/S45，同类故障上可把「已跑失败」从 3 降到 0。
2. **量化/权重完整性探针**（非仅 completion 症状）—— 抬升 S23/S24 从 L1 到「哪类张量」提示。
3. **三层率日志与评分一致化** —— identical-mode vs unique-mode 分列，避免 precision=0 被误读成「无异常」。
4. **L2 规则库持续 ≠ 扩展** —— v1.2→v5.8 约 47 版本叙事；ones/zeros/abs/mag 矩阵仍可补（更多 bias/组合）。
5. **L3 流水线产品化** —— dump_dir 重映射 + 标准 ref-kv 模板，把 S10′/S12/S30 从「潜力」变默认可跑。
6. **覆盖空洞** —— HARD-DEFER 场景（CP/PD/hybrid/spec edge）需单独环境议程，不靠 soft-inv 刷分。
7. **false GAP 防护** —— 已有：有 `token_repeat` 时勿因 samples 偶发 garbage 标签宣 GAP；固化到 score 脚本。

---

## 9. 汇总

### 9.1 按结局

| 结局 | 数量 | 说明 |
|------|------|------|
| PASS · detect + L2 | ~137–140 | 主体，含 soft-inv 与部分真实类 |
| PASS · detect-only（L1） | 2 | S23, S24 |
| FAIL + GAP | 3 | S01, S07, S45（有限垃圾） |
| INVALID | 1 | S44 |
| 未跑 / HARD / BLOCKED / skip | ~10 | S02–S05, S09, S13, S15, S21, S27 等 |

### 9.2 最终判断（给决策者）

1. **值得继续投入** soft-inverse / 算子回归语料 + L2 skills 爬山（已规模化至 S152）。
2. **下一里程碑是 detector**，不是更多 ones/zeros 变体刷分；否则 GAP 列表不会缩短。
3. **对外表述**坚持：「高检出的可复现算子故障定界网」，而非「通用幻觉/垃圾文本检测器」或「自动根因定位」。
4. origin-faithful 协议有效：避开 amplifier 虚高；S44/S45 的处理是诚实信号。

### 9.3 噪声 / 覆盖缺口

- 未做独立 clean-run 假阳大规模统计（缺口）。
- Soft-inv 为人工注入：高检出**不自动等于**生产假阳低。
- 家族覆盖以 RMSNorm / logits·sampler / RoPE·pos / attn / SwiGLU 最密。

---

## 10. 证据索引

| 产物 | 位置 |
|------|------|
| 能力矩阵 | 内部仓 `runtime-guard-test/docs/anomaly-skills-capability-20261017.md` |
| 技能元数据 | 内部仓 `runtime-guard-test/analysis/skill/SKILLS_METADATA.md`（评估时 v5.8） |
| Mining 政策 | 内部仓 `runtime-guard-test/docs/anomaly-mining-policy-pr-rooted-20261018.md` |
| 验证环 | 内部仓 `runtime-guard-test/docs/anomaly-skills-verify-loop-20261017.md` |
| 场景证据 | 内部仓 `runtime-guard-test/tests/build-anomaly-env/fail-evidence/Sxx/` |