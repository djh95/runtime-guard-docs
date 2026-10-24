---
name: build-anomaly-env
description: >-
  Build origin-faithful anomaly environments (overlay-only) for Runtime Guard
  detector evaluation. Mine PR-rooted typed bugs, raise repro via allowed knobs
  only (no NaN/token-fill amplifiers), record three-layer rates, package
  SPEC/overlay/samples. Post-repro delimitation → investigation / ref-kv-dump;
  do not duplicate the 十问 here.
---

# build-anomaly-env（构建异常环境）

**类型：构造 / 评测基建。** Agent 面向：从真实 bug/PR 挖候选 → 写 overlay → 抬复现率 → 记三层 → 打包。  
**不是**用户手册；结案定界（十问）交给 [`investigation`](../investigation/SKILL.md) / [`ref-kv-dump`](../ref-kv-dump/SKILL.md)。

契约：[SKILLS_METADATA.md](../SKILLS_METADATA.md) · keep-set 包形：[04](../../04_case_studies/README.md)

---

## 忠于原 bug 逻辑（origin-faithful）

**一句话：** 注入逻辑必须与原 bug 相同；禁止用 NaN 强写、token `fill_`、或其它「伪造症状」手段来凑检出。

用户面不必背这个英文词——在案例规格/构造节用白话写清即可。稳定缩写（三层率、overlay、keep-set…）见 [短词汇表](../../04_case_studies/词汇表.md)。

与表格字段 **Origin**（`vllm-only` / `both` / `ascend-only`）是两件事——Origin 标代码树，本条标复现纪律。

---

## When / Not

| 用本 skill | 不用 |
|------------|------|
| 挖/建 anomaly 场景，抬 origin-faithful 复现率 | 排障编排 / 十问定界 → `investigation` |
| 写 SPEC、overlay、三层计数、上游锚点 | 已有异常后抓 ref KV → `ref-kv-dump` |
| keep-set 打包（overlay + 规格） | 接线 backport → `apply-mrv*` |

---

## 硬约束（必守）

### 1. origin-faithful

- **同逻辑**：overlay 复现的是原 bug 的触发谓词 / 错误路径，不是「看起来像坏输出」。
- **禁止：** `nan`/`inf` 强写 logits/KV；`fill_` / 重复 token 填输出；改计算以**发明**症状的合成放大器。
- **仅放大剂跑通 ≠ PASS。**

### 2. 故障只走 overlay

- **禁止**改 canonical 产品树当「场景」。
- 测试仓目录类：`tests/build-anomaly-env/`（构建异常环境）。
- docs keep-set 必带：`evidence/overlay.patch` + `evidence/规格说明.md`（勿只链外部仓库当实质）。

### 3. 成功判据

成功 = **detector / report / dump**（及三层率），**不是** GSM8K / golden / 业务准确率。  
detector 漏检 → 记 FAIL+GAP / 缺口，**禁止**用放大器硬凑 detect。

### 4. 三层（trigger ≠ precision ≠ detect）

| 层 | 含义 | 证据 |
|----|------|------|
| **trigger** | bug 路径真正打中 | overlay 日志 / `ANOMALY_TRIGGER` 等计数 |
| **precision** | 输出/数值已异常（可无 report） | samples、评分脚本、形态核对 |
| **detect** | 已合入 detector 出 report | `report_*.json` 计数 |

**overlay 必须在 bug 路径开火时打日志**（计数 + 关键上下文）。三层分别记 rate；勿把 trigger 当 detect。

### 5. 抬复现率：只允许 knobs

白盒后在 SPEC 列 **allowed / forbidden knobs**。

| 允许（抬命中同谓词的概率） | 禁止 |
|---------------------------|------|
| KV-cache 大小 / util | 伪造 tensor / NaN / fill token |
| 阈值 / guards | 改计算发明症状 |
| batch / seq 长度 | soft-inv 刷分（ones/zeros/abs pad 凑分） |
| 请求量 / 并发 / 时长 | 用 `synthetic/` 冒充主门 |
| seeds / 调度边 / 同路径并行拓扑 | |

时间：优先 **≤5–10 min 大量请求**；稀有路径可拉长，**单场景上限约 1h**。超时未复现 → 记 **未复现**（附 knobs），勿放大器硬凑、勿空耗。  
每场景记 **original repro rate**（调前）与 **tuned repro rate**（调后）及所用 knobs。

### 6. HARD / DEFER；多挖少造

- 难复现（双机 HCCN、稀有拓扑、无安全 knobs）→ 标 **HARD/DEFER**，**继续挖候选**，勿上放大器。
- 优先 **both** / **ascend-only** 起源；`vllm-only` 降权（Ascend 常改写该路径）。
- **PR-rooted + typed**：一真实修复 PR → 一类根因；同类勿堆太多。硬 bug 标 HARD，勿用 soft-inv 顶替刷分。
- 新旧 precision 修复 PR 都可挖；扩根因面（算子溢出、PD/KV 错写、权重/量化等）。

### 7. 每场景交付物

| 交付 | 要求 |
|------|------|
| SPEC / 规格说明 | Origin 标签、上游 fix PR、allowed/forbidden knobs、`repro_mode`（`origin` \| `origin_tuned` \| `blocked` \| `hard_defer`）、期望 detector |
| overlay | 可应用 patch；开火日志 |
| 上游锚点 | 根因修复 PR（多笔时标明角色） |
| 三层计数 | trigger / precision / detect（及 original vs tuned rate） |
| 原始异常样本 | completions / logs / dumps（FAIL 时尤须：确认是否复现 + 若干 raw 样本） |
| keep-set 打包 | 包内 `overlay.patch` + `规格说明.md`；结案入口在 `cases/Sxx/README.md` |

**构造 vs 复现技巧（文案落点）：** 「勿强制写 NaN / token fill」属 **overlay 构造**，写在规格 / 根因·构造；**不要**放进案例 README 的「复现技巧」（复现技巧 = 怎么跑才对齐本包结论）。origin-faithful 同属本 skill，不是用户面复现技巧。

**无实测则留空：** keep-set 未跑或证据不可信时，只留 overlay+规格；结案/三层/samples/reports/`kv_compare` **留空或删除**，勿半截旧跑、勿编造。重测后 **同一次异常请求** 回填（见 `investigation` 证据完整性）。

**抓 dump：** detector 未亮时可用 `manual_dump` 当场抓有效异常 KV；N = 目标总次数（进程内计数，≥N 停）。短 output 也能 dump，但弱窗（如 o=1）不作有效对账前提。

### 8. `synthetic/` / g_inject

**阳性对照 only**，不是主门集 / ~10-gate 主体。勿用其 PASS 代替 origin-faithful 场景。

### 9. 复现之后（交叉链接，勿在此展开十问）

有异常证据后 → [`investigation`](../investigation/SKILL.md) 编排；verify PASS 后 → [`ref-kv-dump`](../ref-kv-dump/SKILL.md)。  
结案用 **四档**（未复现 / 复现未抓到 / KV 一致→排除 / KV 不一致→定界），勿把本 skill 的 PASS/FAIL 语言升格为 keep-set headline。  
**本 skill 不写十问推断纪律。**

---

## 工作流（密）

1. **挖** PR（vLLM / vllm-ascend；含较旧修复）→ 定 type / Origin → 易抬率优先。  
2. **白盒** 触发谓词 → 列 allowed/forbidden knobs → 写 overlay（同逻辑 + 开火日志）。  
3. **基线跑** → 记 original rates；调 knobs → 记 tuned rates（时限内多请求）。  
4. **判** 三层；漏检记 GAP；未复现记 FAIL（附 raw 证据），勿空口 FAIL。  
5. **HARD** 则停该候选、换下一个。  
6. **打包** SPEC + overlay + 三层 + samples；进 docs keep-set 时带齐 overlay+规格。  
7. 定界需求 → 交 investigation / ref-kv。

## Pin / 模型（偏好）

- Guard pin：G2（A+#18644）类钉点，场景间可比。  
- 模型优先已跑通：DeepSeek-V2-Lite、Qwen3-8B、Qwen3.8-27B。  
- PD：优先同机 1P1D；无跨机 HCCN 路径时勿硬上。

## Related

- 编排 / 十问：`investigation`  
- 标杆 KV：`ref-kv-dump`  
- 读 report：`analysis`  
- 用户向案例包：`04_case_studies/`（勿在此重复用户教学）
