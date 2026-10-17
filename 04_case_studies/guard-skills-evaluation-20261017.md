---
cursor:
  subagentId: "bc-fea3f65c-820d-58a1-a9ad-17d3943fe455"
---

# Runtime Guard × Skills 评估报告（至 S152 / skills v5.8）

**日期：** 2026-10-18  
**范围：** origin-faithful anomaly 环境 S01–S152；证据来自 `fail-evidence/`、`anomaly-skills-capability-20261017.md`、`SKILLS_METADATA` v5.8、handoff/verify-loop。  
**协议约束：** 不计 force-NaN / `fill_` / `logits.zero_()` 等 amplifier；S44 INVALID 非 skills 胜利。  
**数字口径：** 能力表 152 行；带 `layers.json` 的目录约 142；明确标注处为**估计**。

---

## 1. 总评（Overall verdict）

**结论：对「可复现的算子级 / 采样级 soft-inverse 异常」非常有效；对「有限垃圾文本 / 权重语义 / 未覆盖子系统」仍然弱。**

Runtime Guard + skills 的定位应理解为：

| 用途 | 有效性 |
|------|--------|
| **在线检出**塌缩复读、logits 非有限、部分 spec 接受率异常 | **高**（成功复现且已跑环境中 detect>0 ≈ **99%+**） |
| **离线定界到现象类（L2 class-hint）** 并写出 ≠ 相邻 soft-inv | **高**（能力表约 **140/152** 标到 L2） |
| **定位到算子行 / 权重元素 / 上游 commit（L4）** | **基本不能**（locate 列几乎全「否」——设计上限） |
| **捕获有限、多样、非复读垃圾（S01/S07/S45）** | **失败（GAP）** |
| **权重/量化 always-on 故障** | **仅 detect（L1）**，不可定位张量 |

**一句话：** 作为「算子 soft-inverse 回归网 + 排障定界助手」已证明价值；作为「通用错误文本 / 根因定位器」尚未达标。

---

## 2. 检测（Detection）

### 2.1 成功率（detect>0）

| 口径 | 数量 | 比例 |
|------|------|------|
| 能力表「能否检测 = 是」 | **139** / 152 | **91.4%**（含未跑/停泊分母） |
| 能力表已跑且非「未跑」 | 139 / (152−10) ≈ **142 尝试** | **≈97.9%** |
| `fail-evidence` 中 status=PASS 且有 layers | detect>0 **138** / 139 | **99.3%** |
| S25+ PASS（soft-inv 主波，layers 完整） | **126** / 126 | **100%** |

> **估计说明：** 早期 S06/S08/S10′ 等部分目录 `layers.json` 不完整（字段缺失），能力表与 WHY_PASS 仍记 PASS+detect；上表以能力表与 S25+ 完整证据为主。

### 2.2 按症状 / detector 分布（PASS 主 detector）

来自 PASS + layers 的 `detect_by` 主键（取计数最大者）：

| Detector / 症状类 | PASS 场景数（估计） | 说明 |
|-------------------|---------------------|------|
| **`token_repeat`** | **~104** | 主路径：短语/digit/`!!!!`/复读塌缩 |
| **`logits_finite`** | **~24** | 非有限 logits / `!!!!` 类；常与 residual/SwiGLU/norm 极性或爆幅相关 |
| **`spec_acceptance`** | **1**（S22） | 分布性；samples 可「空标签」仍 L2 |
| **无/缺失** | ~10 | 早期归档不全，**非**新 GAP |

### 2.3 检测失败（GAP 清单）

| ID | 现象 | 已武装 detector | 失败原因 |
|----|------|-----------------|----------|
| **S01** | KV skip-zero → 混合脚本垃圾 | `logits_finite` | 输出有限；非 NaN |
| **S07** | W8A8 scale collapse → 相同混合垃圾 | `logits_finite`（`token_repeat` 亦弱） | 有限多样/相同垃圾，非复读窗 |
| **S45** | top-k on `-logits` → **unique** 垃圾 | `token_repeat` + `logits_finite` | unique garbage；identical-mode 低估 precision |

三者同属 **garbled / mixed-script / unique-garbage** 缺口；协议禁止用 NaN amplifier 刷 PASS。

### 2.4 precision=0 但 detect>0（仍算 PASS）

skills 契约：**precision=0 且 detect>0 ⇒ PASS，不是 GAP**。

已知明确写入元数据/能力表的例子（不完全）：S92, S96, S98, S99, S103, S109, S113, S121, S124 等（**≥9** 处 metadata 显式 `precision=0 OK`）。  
含义：identical-mode / unique-mode 低估「肉眼异常」，但 online detector 仍开火——**三层率必须拆开读**。

---

## 3. 定位 / 定界（Localization）

### 3.1 到达层级

| 层级 | 含义 | 规模（能力表） |
|------|------|----------------|
| **L1 detect-only** | 有 report，无稳定 class 叙事 | **2**（S23/S24 权重·量化 always-on） |
| **L2 class-hint** | 现象类 + ≠ 相邻场景 | **~140** |
| **L3 module-bound** | verify + ref-kv 首分歧 | **少 / 潜力**（S10′/S12/S30 等 KV 类「可选 L3」；本波未系统刷满） |
| **L4 root-cause** | 算子行 / commit | **0（超出 skills）** |

**locate 列：** 能力表几乎全部为「否」（~142「否」+ 未跑「—」）——与设计一致：skills **定界不停在根因**。

### 3.2 ≠ 区分力

- Soft-inverse 波（约 **109** 个 WHY_PASS 显式 soft-inverse）普遍带 **≠ 同模块相邻 mag/polarity/zeros/ones/abs** 行。  
- 区分力来源：overlay 位点 + 症状字符串（如 `pl` / `[code` / `造假` / `!!!!`）+ detector 选型（`token_repeat` vs `logits_finite`）。  
- **典型深度：** 症状类 / 模块族（RoPE、RMSNorm、SwiGLU、attn、residual、embed、logits）——**不是**单行 Triton/NPU kernel 归因。

### 3.3 弱定界

- S23/S24：detect-only，禁止「定位到 layer/scale」。  
- S01/S07/S45：仅离线 score 弱 L2 提示，无 online 胜利。  
- Spec（S22）：靠 rate，不靠文本 GAP。

---

## 4. 能解决的问题类型（CAN）

| 家族 | 代表场景 | 典型 detector | skills 到达 |
|------|----------|---------------|-------------|
| **RMSNorm**（x/out/weight/bias/eps） | S26,S38,S66,S70–S74,S86–S89,S96,S100,S102,S110,S116,S120,S123,S136,S145,S150,S152… | `token_repeat` 或 `logits_finite` | L2 |
| **Residual** pre/post mag/polarity/abs/zeros/ones/leak | S31,S48,S55,S64,S88–S91,S93–S94,S97,S106,S119,S125,S129,S135,S140,S144… | 同上 | L2 |
| **SwiGLU** in/out/gate/up | S39,S50,S56,S67,S72,S76,S81,S103,S107,S115,S121,S131,S133,S143,S146… | 同上 | L2 |
| **Attn Q/K/V / scale / causal / out** | S34–S35,S41,S47,S49,S51–S54,S58–S60,S63,S68,S83,S109,S111,S114,S117–S118,S130,S132,S141–S142,S148–S149… | 多为 `token_repeat` | L2 |
| **RoPE / positions / cos_sin** | S25,S28,S37,S40,S42,S57,S79–S82,S84,S101,S104–S105,S113,S128,S134,S139,S147… | `token_repeat` | L2 |
| **Embed / hidden / logits / sampler** | S36,S43,S46,S53,S61,S65,S69,S80,S85,S92,S95,S98–S99,S108,S112,S122,S124,S126–S127,S137–S138,S151… | `token_repeat`（偶发 finite） | L2 |
| **Overflow / softcap / bang 塌缩** | S20,S33,S38… | `token_repeat` / `logits_finite` | L2 |
| **MoE 路由类** | S06,S16–S19 | `token_repeat` | L2 |
| **Spec resample / SALT** | S22 | `spec_acceptance` | L2 |
| **KV/slot/pad/MLA（部分）** | S08,S10′,S11,S12,S14,S30,S32 | `token_repeat`（+可选 L3） | L2（L3 潜力） |

共同特征：**单一、可触发、可复现的张量变换**；症状落在复读窗或非有限 logits。

---

## 5. 不能 / 弱（CANNOT）

| 类型 | 代表 | 原因 |
|------|------|------|
| **有限垃圾 / unique garbage** | S01, S07, S45 | 缺 garbled/semantic detector |
| **权重·量化 always-on** | S23, S24 | 仅 L1；不可指张量 |
| **INVALID amplifier** | S44 `logits.zero_()` | 协议拒收 |
| **HARD / 基础设施阻塞** | S02/S03/S04/S05/S09/S13/S21/S27… | 未跑或环境/依赖阻塞（CP、HCCN、FLA、spec HARD 等） |
| **真·偶发 / 低概率竞态** | （本语料薄） | 48-req 温启动网捕不到则无 PASS |
| **纯采样 skip 且跨请求极端多样** | 部分 precision=0 场景 | detect 可救；若 detect 也灭则变 GAP（S45） |
| **PD / 跨机 KV 传输** | S04 等 | 覆盖薄 / HCCN |
| **根因级定位** | 全体 | 超出 skills 合同 |

---

## 6. 优化空间（按优先级）

1. **新 detector：garbled / mixed-script / unique-garbage / identical-across**  
   - 直接解锁 S01/S07/S45；预计把「已跑失败」从 3 降到 0（在同类故障上）。  
2. **量化/权重完整性探针（非仅 completion 症状）**  
   - 提升 S23/S24 从 L1→可行动的「哪类张量」提示（仍未必到元素）。  
3. **三层率日志与评分一致化**  
   - identical-mode vs unique-mode 分列；避免 precision=0 被误读成「无异常」。  
4. **L2 规则库持续 ≠ 扩展**  
   - 已有 v1.2→v5.8 约 **47** 个版本叙事；ones/zeros/abs/mag 矩阵仍可补（例如更多 bias/组合）。  
5. **L3 流水线产品化**  
   - dump_dir 重映射 + 标准 ref-kv 模板；把 S10′/S12/S30 从「潜力」变成默认可跑。  
6. **覆盖空洞**  
   - HARD-DEFER 场景（CP/PD/hybrid/spec edge）需单独环境议程，不单靠 soft-inv 刷分。  
7. **false GAP 防护**  
   - 已有：有 `token_repeat` 时勿因 samples 偶发 garbage 标签宣 GAP；继续固化到 score 脚本。

---

## 7. 其他指标与过程信号

### 7.1 三层率（trigger / precision / detect）

- **trigger：** overlay 命中次数；可 >> n_req。  
- **precision：** identical-mode 常低估 unique garbage（S45）或 rambling（S92 等）。  
- **detect：** 排障「能否报警」的主指标；本语料上与 PASS 强对齐。  
- **实践规则：** 先看 detect；再用 precision/score 标签解释症状；trigger 只证明注入发生。

### 7.2 噪声 / 误报

- 未做独立 clean-run 假阳大规模统计（**缺口**）。  
- 已知风险：score 标签曾对「已有 detect」误提示 GAP（S20/S24 等已在 verify-loop 修正）。  
- Soft-inv 为人工注入：高检出**不自动等于**生产假阳低。

### 7.3 覆盖广度

- 能力表 **152** 场景 ID；PASS 覆盖至 **S152**（handoff PASS 桶至 S46–S152 + 早期 PASS）。  
- 未跑/停泊 **~10**；FAIL+GAP **3**；INVALID **1**。  
- 家族覆盖以 **RMSNorm / logits·sampler / RoPE·pos / attn / SwiGLU** 最密（WHY_PASS 关键词粗分）。

### 7.4 Skills 版本爬山（v1.2 → v5.8）

- Metadata 记录约 **47** 个版本条目；近端以「每 3 个 PASS 一波 L2」推进（v5.0–v5.8）。  
- 信号：每波 Inbox PENDING → 同 evidence re-verify → 双仓 main 同步；**闭环可重复**。  
- **估计成本：** 单波（3 场景）离线 analyze+文档+双推 ≈ 一次 skills agent 回合；不含 160 造环境。

### 7.5 可复现旋钮

- 有效：固定模型路径、temp=0、n_req=48、双卡、双 detector、slim fail-evidence。  
- 限制：precision identical-mode；部分场景 detect 略 < n_req（如 S147=47）仍 PASS。

---

## 8. 汇总表

### 8.1 按结局

| 结局 | 数量 | 说明 |
|------|------|------|
| **PASS · detect + L2** | **~137–140** | 主体；含 soft-inv 与部分真实类场景 |
| **PASS · detect-only（L1）** | **2** | S23, S24 |
| **FAIL + GAP** | **3** | S01, S07, S45 |
| **INVALID** | **1** | S44 |
| **未跑 / HARD / BLOCKED / skip** | **~10** | S02–S05,S09,S13,S15,S21,S27 等 |

### 8.2 顶症状 / detector

| 类 | 规模 |
|----|------|
| `token_repeat` | ~104 PASS 主检出 |
| `logits_finite` | ~24 |
| `spec_acceptance` | 1 |
| GAP（有限垃圾） | 3 |

### 8.3 开放 GAP（优先实现）

1. Garbled / unique-garbage / identical-across detector → S01/S07/S45  
2. 权重/scale 完整性（抬升 S23/S24）  
3. L3 ref-kv 默认路径  
4. Clean-run 假阳基线测量  

---

## 9. 证据索引

| 产物 | 位置 |
|------|------|
| 能力矩阵 | `docs/anomaly-skills-capability-20261017.md` |
| 技能元数据 | `analysis/skill/SKILLS_METADATA.md`（v5.8） |
| 验证环 | `docs/anomaly-skills-verify-loop-20261017.md` |
| 场景证据 | `tests/build-anomaly-env/fail-evidence/Sxx/` |
| 仓 tip（评估时） | test `b81e4b1` · docs `a380183` |

---

## 10. 最终判断（给决策者）

1. **值得继续投入** soft-inverse / 算子回归语料 + L2 skills 爬山——已证明可规模化（至 S152）。  
2. **下一里程碑应是 detector**，不是更多 ones/zeros 变体刷分；否则 GAP 列表不会缩短。  
3. **对外表述**应坚持：「高检出的可复现算子故障定界网」，而不是「通用幻觉/垃圾文本检测器」或「自动根因定位」。  
4. origin-faithful 协议有效：避免了 amplifier 虚高；S44/S45 的处理是诚实信号。
