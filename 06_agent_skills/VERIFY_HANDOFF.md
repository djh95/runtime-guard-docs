---
title: Skills verify handoff — 15 typical anomaly cases
date: 2026-10-19
audience: other agents (offline skills verification)
skills_pin: v5.9 / SKILLS_METADATA.md
keep_set: typical-cases-keep-set-20261019.md (N=15)
---

# Skills verify handoff（给其他 Agent）

## 1. Goal

对公开 **15 个典型异常场景（keep-set）** 做一次 **离线 skills 复核**，产出**结构化结果**，供本 Project 后续优化 skills（detector 映射、class-hint、≠ peers、GAP 话术）。

| 要做 | 不要做 |
|------|--------|
| 用已落盘 evidence + 历史 runs，按 5 个 skill 契约复盘 | 新挖 bug / 扩 C 类 soft-inv 刷分 |
| 对照「期望 detect / L 级 / GAP」判 PASS·FAIL | 为刷 PASS 改 overlay / 造 NaN·`fill_` |
| 写清 gaps + 一句 skill lever 建议 | 宣称 L4 / 根因 commit |
| 结果落到约定路径（见 §6） | 占 **builder 机** 卡做 builder 重跑（默认） |

**成功标准：** 15/15 各有一条 JSON + 一篇短 MD；另有一份 rollup；本 Project 能据此改 `investigation` / `analysis` 而不必重读 FE 原文。

---

## 2. Repos / machines（诚实约定）

| 角色 | 主机习惯 | 做什么 | 不要做什么 |
|------|----------|--------|------------|
| **Skills / verify** | **skills 机** | 读仓、跑离线脚本、写 verify 结果 | **不要抢 builder 机卡** |
| **Builder / live repro** | **builder 机** | 起服、打 overlay、写 FE | verify 默认**不**在这里重做 |

**本轮默认 = 纯离线**（skills 机或任意能 clone 两仓的机器即可；**不需要 NPU** 也能完成 analysis 读盘路径）。

仅当 FE 缺 report/samples、或要对齐「现网 skill 是否仍能检出」时，才申请 **builder 机** 按 PRINCIPLES **live 复开**（见 §4）。

### 仓库

```bash
# docs（公开手册 + skill 权威副本 + 15 模版）
git clone git@github.com:djh95/runtime-guard-docs.git   # 或公开 HTTPS

# test（内部仓：脚本 + FE + 满量 runs；需权限，HTTPS 对外 404）
git clone git@github.com:djh95/runtime-guard-test.git   # 有权限用 SSH；勿发公开 blob 链接

export RG_DOCS=/path/to/runtime-guard-docs
export RG_TEST=/path/to/runtime-guard-test
export PYTHONPATH="$RG_TEST"
```

- Skills **公开权威**：`$RG_DOCS/06_agent_skills/`（SKILLS_METADATA **v5.9**）。内部镜像：`$RG_TEST/analysis/skill/`（可 rsync 回写；勿假设时刻 bit-identical）。
- 离线脚本：`$RG_TEST/analysis/scripts/`（`summarize_reports` / `score_completion_samples` / `verify_request_kv` / …）。
- 模型权重 / 卡号：离线复核**不依赖**；live 复开时沿用各 FE `status.json` / SPEC 中的 MODEL·TOPO（常见 Qwen3-8B TP2、DeepSeek-V2-Lite MLA 等）——**以 FE 为准，勿臆造**。

Project Agent Store（本会话结果落点，非公开 Git）：

`/cursor/stores/bc-de323550-4200-4fe6-ba84-cdd9807d574d/`  
（本机绝对路径：`…/AgentStores/cursor_agent_stores/bc-de323550-4200-4fe6-ba84-cdd9807d574d/files/`）

---

## 3. Exact paths

### 3.1 Skills（跑哪 5 个）

| Skill | Path（docs） | 本轮用法 |
|-------|--------------|----------|
| **investigation** | `06_agent_skills/investigation/SKILL.md` | 编排：按契约输出 detect / L / class / ≠ |
| **analysis** | `06_agent_skills/analysis/SKILL.md` | **主路径**：读 FE report/samples，跑脚本 |
| **detector-sweep** | `06_agent_skills/detector-sweep/SKILL.md` | 仅当 live 复开且类别未知（本轮通常跳过） |
| **config-recommender** | `06_agent_skills/config-recommender/SKILL.md` | 仅 live；离线可对照 FE 里当时 config 是否合理 |
| **ref-kv-dump** | `06_agent_skills/ref-kv-dump/SKILL.md` | 仅当 FE 有完整 dump **且**要验 L3；keep-set 多数停 L1/L2，**默认不做** |

契约：`06_agent_skills/SKILLS_METADATA.md`（当前 **v5.9**）。  
镜像：`$RG_TEST/analysis/skill/`。

### 3.2 典型案例文档（15）

`$RG_DOCS/04_case_studies/cases/Sxx/`（`S10′` → **`S10p/`**；FE 目录仍是 `S10/`）

| ID | 包 |
|----|-----|
| S01 | `cases/S01/` |
| S10′ | `cases/S10p/` |
| S11 | `cases/S11/` |
| S07 | `cases/S07/` |
| S23 | `cases/S23/` |
| S45 | `cases/S45/` |
| S43 | `cases/S43/` |
| S22 | `cases/S22/` |
| S06 | `cases/S06/` |
| S26 | `cases/S26/` |
| S25 | `cases/S25/` |
| S50 | `cases/S50/` |
| S48 | `cases/S48/` |
| S47 | `cases/S47/` |
| S33 | `cases/S33/` |

索引：`04_case_studies/README.md`

### 3.3 Evidence / runs / 政策指针

| 内容 | Path |
|------|------|
| Fail-evidence | `$RG_TEST/tests/build-anomaly-env/fail-evidence/Sxx/`（S10′ → **`S10/`**） |
| Skills runs 归档 | `$RG_TEST/docs/anomaly-skills-runs/`（如 `S01-20261017.md`；S10′/S11 可能在 `batch-pass-wave-*.md`） |
| Capability 矩阵 | `$RG_TEST/docs/anomaly-skills-capability-20261017.md`（公开仓仅为 stub） |
| Principles | `$RG_DOCS/04_case_studies/anomaly-PRINCIPLES.md`（镜像 test `tests/build-anomaly-env/PRINCIPLES.md`） |
| Mining policy | `$RG_TEST/docs/anomaly-mining-policy-pr-rooted-20261018.md` |
| Verify loop 旧笔记 | `$RG_TEST/docs/anomaly-skills-verify-loop-20261017.md` |
| Builder handoff（builder 机↔skills 机） | `$RG_TEST/docs/anomaly-skills-handoff.md`（内部私有） |
| Overlay / MATRIX | `$RG_TEST/tests/build-anomaly-env/{README,MATRIX,INJECTION,PRINCIPLES}.md` + 各 `NN_* / SPEC` |

FE 内常见文件：`layers.json` · `status.json` · `WHY_PASS.md` / `WHY_UNDETECTED.md` · `sample_*.json` · 尝试子目录（含 report/dump 痕迹）。

---

## 4. 如何构造 / 复开 anomaly env（verify 优先离线）

1. **优先离线：** 只读 §3.3 FE + runs + `cases/Sxx/`；用 `PYTHONPATH=$RG_TEST` 跑 analysis 脚本。  
2. **协议：** 任何 live 复开必须遵守 `anomaly-PRINCIPLES.md`（origin-faithful；禁止 NaN/`fill_` 放大器）。  
3. **Live 仅当：** FE 无可用 samples/report、或要确认「当前 skill 文案 vs 现网 detector」；走 builder 机，参考各场景 `SPEC.md` / overlay 与 `tests/build-anomaly-env/scripts/sNN_*_concurrent_repro.py`（若存在）。  
4. **不要**为 verify 批量重跑 S51–S152 C 类矩阵。

---

## 5. Verification procedure（每个 ID 重复）

对 keep-set 每个 `scenario_id`：

1. **读案例包** `$RG_DOCS/04_case_studies/cases/Sxx/` → 记下期望 detect / L / GAP / 对照 peer。  
2. **读 FE** `$RG_TEST/tests/build-anomaly-env/fail-evidence/Sxx/`（S10′→`S10/`）：`layers.json`、WHY_*、samples。  
3. **读历史 run** `$RG_TEST/docs/anomaly-skills-runs/Sxx-*.md`（或 batch 文件中对应段落）。  
4. **跑 analysis（能跑则跑）**  
   ```bash
   PYTHONPATH="$RG_TEST" python -m analysis.scripts.score_completion_samples --sample-dir <FE samples 目录>
   # 若有 report JSON：
   PYTHONPATH="$RG_TEST" python -m analysis.scripts.summarize_reports --report-dir <report_dir>
   ```  
5. **按 investigation 契约自评**（不必真起服）：  
   - detect 是否命中期望 detector（或 GAP 期望 miss）  
   - L1–L4 是否与期望一致（多数 L2；S23=L1；GAP=弱 L2 / 无 online detect）  
   - class-hint 与 **≠ peers** 是否写对（对照 capability / investigation 表）  
6. **判 verdict：** `match_expected` | `false_gap` | `wrong_class` | `overclaim_L` | `missing_differentiator` | `stale_evidence`  
7. **写一条结果**（§6 schema）+ 一句 `suggested_skill_lever`。  
8. **禁止：** 改 FE；宣称 L4；把 GAP 用放大器「修成」PASS。

顺序建议（对照课成对）：  
`S01 → S10′ → S11` · `S07 → S23` · `S45 → S43` · `S22` · `S06` · `S26 → S25` · `S50 → S48 → S47 → S33`。

---

## 6. Required output schema

### 6.1 落盘约定（Project store）

```text
internal/skills-verify-results/2026-10-19/
  README.md                 # 本轮说明 + agent id
  rollup.json               # 15 条数组 + summary
  rollup.md                 # 人读表
  cases/
    S01.json
    S10p.json               # S10′ 文件名用 S10p
    …
```

公开 Git **不要**提交满量 JSON；需要时可在 docs 只留本 handoff。优化 skills 时由协调 agent 读 store。

### 6.2 Per-case JSON（必填字段）

```json
{
  "scenario_id": "S01",
  "evidence_path": "tests/build-anomaly-env/fail-evidence/S01/",
  "case_doc": "04_case_studies/cases/S01/",
  "skills_version": "v5.9",
  "verify_mode": "offline",
  "expected": {
    "detect": false,
    "detector": null,
    "level": "GAP",
    "class_hint": "finite mixed-script garbage / KV skip-zero",
    "notes": "GAP case: miss is success"
  },
  "observed": {
    "detect": false,
    "detector": null,
    "level": "weak_L2_samples",
    "class_hint": "…",
    "neq_peers": ["S10p", "S07", "S45"]
  },
  "verdict": "match_expected",
  "gaps_found": [],
  "suggested_skill_lever": "Keep GAP wording; do not treat samples-only as online detect.",
  "raw_snippets": {
    "layers": {"trigger": 0, "precision": 0, "detect": 0},
    "report_keys": [],
    "sample_completions": ["…≤200 chars…"]
  },
  "agent_id": "<verifying-agent-bcId>",
  "verified_at": "2026-10-19T…"
}
```

`level` 枚举建议：`GAP` | `L1` | `L2` | `L3` | `L4` | `weak_L2_samples` | `unknown`。  
`verdict` 见 §5。GAP 场景：**期望 miss** → `detect=false` 且 `verdict=match_expected`。

### 6.3 Rollup

`rollup.json`：

```json
{
  "date": "2026-10-19",
  "skills_version": "v5.9",
  "keep_set_n": 15,
  "summary": {
    "match_expected": 0,
    "false_gap": 0,
    "wrong_class": 0,
    "overclaim_L": 0,
    "missing_differentiator": 0,
    "stale_evidence": 0
  },
  "cases": ["<per-case objects or paths>"],
  "top_levers": ["…", "…", "…"]
}
```

---

## 7. Keep-set 15 — expected outcome

| ID | Type | Expected detect | Expected level | 对照 / 备注 |
|----|------|-----------------|----------------|-------------|
| **S01** | KV·PD·pad | **miss（复现未出现）** | **FAIL（复现未出现）**（非 GAP；CJK 排除后 precision=0） | vs S10′ 能检；见 `cases/S01/` |
| **S10′** | KV·PD·pad | `token_repeat` | **L2**（L3 潜力勿强制） | FE=`S10/` |
| **S11** | KV·PD·pad | `token_repeat` | **L2** | ≠ recycle；pad-tail |
| **S07** | Quant·weight | **miss（GAP）** | **FAIL+GAP** | S07=有乱码+漏检；S01=复现未出现（根因亦不同） |
| **S23** | Quant·weight | `token_repeat` | **L1 only** | 勿抬到 L2 元素 |
| **S45** | Embed·logits·sampler | **miss（GAP）** | **FAIL+GAP** | unique garbage；≠S01 |
| **S43** | Embed·logits·sampler | `token_repeat` | **L2** | vs S45 |
| **S22** | Spec | **`spec_acceptance`** | **L2** | 非文本主路径 |
| **S06** | MoE | `token_repeat` | **L2** | 唯一 MoE 模版 |
| **S26** | RMSNorm | `token_repeat` | **L2** | PR #42379 |
| **S25** | RoPE·positions | `token_repeat` | **L2** | PR #7082；≠S11 |
| **S50** | SwiGLU | `logits_finite` | **L2** | `!!!!` |
| **S48** | Residual | `logits_finite` | **L2** | negate；≠S31/S38 |
| **S47** | Attn | `token_repeat` | **L2** | K/V swap 等 |
| **S33** | Overflow·softcap | `token_repeat` | **L2** | ≠S20 overflow 叙事 |

三层率数字以各 FE `layers.json` / 模版归档为准；上表是 **skills 期望语义**，不是要求重跑出相同整数。

---

## 8. 完成后交给协调方

1. Store 路径：`internal/skills-verify-results/2026-10-19/rollup.md` + `rollup.json`  
2. 列出 `verdict != match_expected` 的 ID + `suggested_skill_lever`  
3. **不要**直接改 skills 合入 main，除非协调方明确授权；本 handoff 的产出是优化输入。

---

## 9. Quick link map

| 需要 | 打开 |
|------|------|
| 本文件（docs） | `06_agent_skills/VERIFY_HANDOFF.md` |
| 本文件（store） | `docs/skills-verify-handoff-for-agents-20261019.md` |
| 15 个案例包 | `04_case_studies/cases/Sxx/` |
| Skills | `06_agent_skills/*/SKILL.md` |
| FE（内部私有；满量） | `$RG_TEST/tests/build-anomaly-env/fail-evidence/Sxx/`；对外对照用本仓 `04_case_studies/cases/Sxx/evidence/` |
| Runs（内部私有） | `$RG_TEST/docs/anomaly-skills-runs/`（公开仓不附满量归档） |
