---
name: runtime-guard-investigation
description: >-
  Orchestrate end-to-end runtime_guard debugging: triage whether Guard fits,
  collect inputs, delegate to detector-sweep / config-recommender / analysis /
  ref-kv-dump, then deliver 10-question KV delimitation (not root-cause). Do
  not invent runtime_config thresholds or reimplement offline/ref scripts.
  Native dump_kv for Guard KV path; logits_finite → still KV (finite/unused-zero),
  msprobe last. Align with handbook 02.
---

# runtime_guard investigation（编排总控）

**类型：编排。** 只做 triage、收集输入、委派原子 skill、汇总定界交付。  
底层配置 / 读盘 / force-feed / KV 对比 **委派**，不在本 skill 重写一遍。

手册：[02](../../02_problem_localization/README.md) · [01](../../01_enable_and_start/README.md) · [03](../../03_detectors/README.md)  
契约：[SKILLS_METADATA.md](./SKILLS_METADATA.md)  
离线脚本：本仓 [`../scripts/`](../scripts/)（完整评测矩阵不在本仓）  
产品：`vllm_ascend/observability/runtime_guard/`（[#16849](https://github.com/vllm-project/vllm-ascend/pull/16849)/[#18644](https://github.com/vllm-project/vllm-ascend/pull/18644)）

**Guard KV 路径：** 对比源只用 native `dump_kv`（勿用 msprobe / 自造 dumper **冒充** KV 对比源）。  
**分流（`logits_finite` 也先 KV）：** 采样前 NaN/Inf 命中后 **仍** 走 `dump_kv` + 标杆。优先查：**有效槽有限 vs Inf/NaN**；再查 **未用槽**：有限非 0=脏写/卫生问题（**通常不致坏结果**），未用槽 **Inf/NaN** 才可能影响结果。对比时**先数值门闩**（NaN/Inf/零范数 → **数值问题**，不算余弦），只在干净格上算余弦/`p+o-1`。有效槽全非有限 / 无有效余弦 → **不定层**。标杆必须**未**触发 `logits_finite`。先判必现；非必现用 `manual_dump`（抓标杆时确认未炸）。**msprobe 殿后**（全程挂钩、开销大，不能检出后再开）。

## 开场必问

1. **运行环境**：容器 / 路径 / `{MODE}` / `{MODEL}` / `{TOPO}` / 卡号  
2. **启动脚本** `{START}` · **请求脚本** `{REPRO}`  
3. **谁跑服务**（确认前不要擅自起服）  
4. **版本**、能否压测、有无清洁标杆、本地是否已有 `report`/`kv_cache`  
5. **（必现时）其他环境是否正常？** 例：厂商环境有问题、自建环境正常 → 可能走**跨环境标杆**（见下；细则 [`ref-kv-dump`](../ref-kv-dump/SKILL.md)）

| Var | 含义 |
|-----|------|
| `{RG_CFG}` | live `runtime_config.json`（绝对路径） |
| `{REPORT}` / `{KV_ROOT}` | 报告根 / `kv_cache` 根 |
| `{MODE}` `{MODEL}` `{TOPO}` | graph/eager、权重、拓扑 |

## Step 1 — Triage

**不适合（换工具，终止）**

| 现象 | 原因 |
|------|------|
| Hang / 死锁 | Guard 依赖集体通信，无法对 hang 做根因定界 |
| 启动 crash | 服务起来后才工作 |
| OOM / 泄漏 | 不监控内存 |
| 纯吞吐下降 | profiling |
| 权重 / 拓扑 / 传输栈错 | 先修配置 |

**适合：** `token_repeat` / `logits_finite` / `spec_acceptance`（MTP）。  
- **`logits_finite` 命中** → 仍委派 [`ref-kv-dump`](../ref-kv-dump/SKILL.md)：有效槽有限性 + 未用槽分级（有限非 0 vs Inf/NaN）+（可算时）余弦；**禁止**因 NaN cos 跳过 KV 或写成「复现未抓到」。KV 分流后再视需要委派 [`msprobe-dump`](../msprobe-dump/SKILL.md)（statistics · eager · **殿后**）。  
- **`token_repeat` / 有限异常且疑 KV** → 同：`dump_kv` + 标杆。  
**勿启用未合入：** `output_substring` / `token_logprob` / `slot_*` / `kv_state`。  
**看似必现：** 先按手册 [02 §4 Step 0.5](../../02_problem_localization/README.md) 做连测 / 换输入（勿只靠 `max_tokens=1`）/ 消融 / PD 单 P·单 D；未验证勿在交付里写「必现」。**并向使用者确认：其他环境是否正常。** 若存在「异常环境 + 正常环境」，可委派 [`ref-kv-dump`](../ref-kv-dump/SKILL.md) **分环境**抓 buggy/ref；对比前必须核对**权重 MD5（或等价）**与**代码 commit（及关键 patch/overlay）一致**——不一致则不能当干净标杆，先对齐。非必现 → `manual_dump`；抓标杆须确认**未**亮 `logits_finite`。

### 三层率（anomaly / 压测必记）

| Layer | 含义 | 证据 |
|-------|------|------|
| **trigger** | overlay / 故障路径真正打到 | `ANOMALY_TRIGGER` 计数、overlay 日志 |
| **precision** | 输出/数值已坏（可无 report） | samples 垃圾文、temp=0 发散、`score_completion_samples` |
| **detect** | 已合入 detector 出 report | `report/<type>/report_*.json` 计数 |

**trigger ≠ precision ≠ detect。** 有 trigger+precision 但 detect=0 → **FAIL+GAP**（记缺口，勿造 NaN/填 token 伪装 PASS）。

### 根因 class → 已合入 detector（来自 easy wave）

| Class（示例 Sxx） | 典型症状 | 主 detector | 备注 |
|------------------|----------|-------------|------|
| MoE 路由/合成/renorm（S06,S16–S19） | 复读、digit/`***`/`ctx` echo、ZWSP | `token_repeat` | 无 MoE 专用 detector |
| KV recycle / packed stride / slot→0（S08,S10′,S12） | 复读、xxxx collapse | `token_repeat` | KV 类；verify+ref 可定界 |
| MLA pad / o_proj empty（S11,S14） | digit/junk、graph pad | `token_repeat` | 间接 KV；dump 路径常有 |
| FIA FULL-graph pad（S32，soft-inv #7144） | **unique** pad-echo（`wN_M…` / `_0_0_0`）；identical-mode 低估 | **`token_repeat`** | **L2**（graph pad keep descriptor）；≠ S14 o_proj empty；score=`pad_echo` |
| Incomplete softcap（S33，÷cap+tanh skip *cap） | digit/`1.1.1…` 复读 | **`token_repeat`** | **L2**（softcap incomplete）；≠ S20 unstable/overflow（`!!!!`/token0） |
| Attn scale drop（S34，1/sqrt(d)→1.0） | unique digit/junk 混杂；identical-mode 低估 | **`token_repeat`** | **L2**（wrong attn temperature）；≠ S20/S32/S33 |
| Causal-off / future leak（S35，causal=False + mask=None） | 强 `phrase_repeat` / prompt-echo 复读 | **`token_repeat`** | **L2**（non-causal / sparse_mode=0）；≠ S34 scale |
| Temp-scale blowup（S36，post-temp ÷50） | unique garbled prose / id-echo；identical-mode 低估 | **`token_repeat`** | **L2**（wrong T scale）；score=`id_echo`/`unique_garbage`；≠ S29/S20 |
| Positions→0 before RoPE（S37） | digit/`333…`/`999…` 复读塌缩 | **`token_repeat`** | **L2**（pos-collapse）；≠ S25 half ≠ S28 style ≠ S11 pad |
| RMSNorm identity skip（S38） | 全请求 `!!!!…`；**logits non-finite** | **`logits_finite` 为主** | **L2**（norm skip）；≠ S26 fp32-mul ≠ S31 residual-drop；≠ S20（S20 常只亮 `token_repeat`） |
| SwiGLU skip-silu（S39，plain gate×up） | 全请求 `!!!!…`；**logits non-finite** | **`logits_finite` 为主** | **L2**（activation skip）；≠ S26/S31/S38 norm 族 |
| RoPE skip（S40，unrotated Q/K） | Nile/`phrase_repeat` 句级复读 | **`token_repeat`** | **L2**（no rotary）；≠ S25 half ≠ S28 style ≠ S37 pos-zero |
| Post-FA attn out `mul_(1000)`（S41） | 全请求 `!!!!…`；**logits non-finite** | **`logits_finite` 为主** | **L2**（wrong attn-out scale）；≠ S34 softmax-scale ≠ S14/S35 |
| RoPE phase negate（S42，`-cos_sin_cache`） | digit/`1.1.1…` 复读 | **`token_repeat`** | **L2**（wrong phase）；≠ S37 pos-zero ≠ S40 skip ≠ S25/S28 |
| Embed scale ×100（S43） | 纯换行塌缩 / newline collapse | **`token_repeat`** | **L2**（wrong embed magnitude）；score=`newline_collapse`；≠ S23/S41 |
| Logits `zero_()` before sample（S44） | `!!!!` token0 | — | **BLOCKED / invalid-synthetic**：force-write logits 发明症状（PRINCIPLES §2）；非 10-gate PASS / 非 skills win |
| Top-k/top-p on `-logits`（S45，bottom nucleus） | **unique** mixed-script garbage；identical-mode 低估 | **当前均弱** | **FAIL+GAP**（同 S07；≠ S01 dense 复现未出现）；`token_repeat`/`logits_finite` miss；勿放大器硬凑 PASS |
| Penalty sign flip（S46，1/rep + neg freq/pres） | digit/`1.1.1…`/`0.0.0…` 复读塌缩 | **`token_repeat`** | **L2**（penalty polarity invert）；真实 sampling soft-inv；≠ S45 GAP ≠ S44 amplifier |
| K/V swap before FA（S47） | 单字/短语复读塌缩（如 `郦…Trail`） | **`token_repeat`** | **L2**（K/V swapped into attn）；≠ S34 scale ≠ S35 causal ≠ S41 attn-out ×1000 |
| Residual negate（S48，`-residual` before add-RMSNorm） | 全请求 `!!!!…`；**logits non-finite** | **`logits_finite` 为主** | **L2**（wrong residual polarity）；≠ S31 drop ≠ S38 skip |
| Attn scale blowup（S49，scale×50） | unique/`1.1.1…` 混杂；identical-mode 低估 | **`token_repeat`** | **L2**（attn temp too hot）；≠ S34 scale→1.0 ≠ S41 post-FA ×1000 |
| SwiGLU gate/up half-swap（S50，`cat(up,gate)`） | 全请求 `!!!!…`；**logits non-finite** | **`logits_finite` 为主** | **L2**（SwiGLU halves swapped）；≠ S39 skip-silu |
| Value scale ×50 before FA（S51） | 复读/`...` 塌缩 | **`token_repeat`** | **L2**（wrong V magnitude）；≠ S41 attn-out ≠ S47 K/V swap ≠ S49 attn-scale |
| Query negate before FA（S52） | unique/garbage 复读混杂 | **`token_repeat`** | **L2**（wrong Q polarity）；≠ S47 K/V ≠ S51 V-scale ≠ S42 RoPE-phase |
| LM-head logits ÷50（S53） | digit/`1.1.1…` 复读 | **`token_repeat`** | **L2**（wrong lm-head scale）；≠ S36 post-temp ÷50 ≠ S44 logits.zero_ |
| Key negate before FA（S54） | unique/garbage 复读混杂 | **`token_repeat`** | **L2**（wrong K polarity）；≠ S47 K/V ≠ S51 V-scale ≠ S52 Q-negate |
| Residual ×50 before add-RMSNorm（S55） | 全请求 `!!!!…`；**logits non-finite** | **`logits_finite` 为主** | **L2**（wrong residual magnitude）；≠ S31 drop ≠ S38 skip ≠ S48 sign-flip |
| SwiGLU input negate（S56，`x=-x` before npu_swiglu） | 全请求 `!!!!…`；**logits non-finite** | **`logits_finite` 为主** | **L2**（wrong SwiGLU input sign）；≠ S39 skip-silu ≠ S50 half-swap |
| Positions ×2 before RoPE（S57） | 短语/`name.` 复读塌缩 | **`token_repeat`** | **L2**（wrong pos magnitude）；≠ S37 pos-zero（negate 会炸 NPU） |
| Value negate before FA（S58） | 全请求 `!!!!…`；**logits non-finite** | **`logits_finite` 为主** | **L2**（wrong V polarity）；≠ S51 V×50 ≠ S47 K/V ≠ S52/S54 Q/K-negate |
| Key ×50 before FA（S59） | digit/`0.0.0…` 复读混杂 | **`token_repeat`** | **L2**（wrong K magnitude）；≠ S49 attn-scale ≠ S51 V×50 ≠ S54 K-negate |
| Query ×50 before FA（S60） | digit/`0.0.0…` 复读混杂 | **`token_repeat`** | **L2**（wrong Q magnitude）；≠ S52 Q-negate ≠ S49/S51/S59 |
| Hidden ×50 before lm-head（S61） | digit/`1.1.1…` 复读 | **`token_repeat`** | **L2**（wrong pre-head hidden mag）；≠ S53 logits÷50 ≠ S43 embed×100 |
| Pre-RMSNorm x×50（S62） | 全请求 `!!!!…`；**logits non-finite** | **`logits_finite` 为主** | **L2**（wrong pre-norm act mag）；≠ S26 fp32-mul ≠ S38 skip ≠ S48/S55 residual |
| Attn-out negate after FA（S63） | 全请求 `!!!!…`；**logits non-finite** | **`logits_finite` 为主** | **L2**（wrong attn-out polarity）；≠ S41 attn-out ×1000 |
| Residual ÷50 before add-RMSNorm（S64） | 短语/`[code` 复读塌缩 | **`token_repeat`** | **L2**（wrong residual mag low）；≠ S48 sign-flip ≠ S55 residual×50 |
| LM-head logits ×50（S65） | digit/`1.1.1…` 复读 | **`token_repeat`** | **L2**（wrong logit mag high）；≠ S53 logits÷50 ≠ S36 temp÷50 |
| RMSNorm weight negate（S66，`-weight` into add-RMSNorm） | 全请求 `!!!!…`；**logits non-finite** | **`logits_finite` 为主** | **L2**（wrong norm-weight sign）；≠ S26 fp32-mul ≠ S38 skip ≠ S48/S55 residual ≠ S62 pre-norm x |
| SwiGLU out negate（S67，`-out` after npu_swiglu） | 全请求 `!!!!…`；**logits non-finite** | **`logits_finite` 为主** | **L2**（wrong SwiGLU out polarity）；≠ S39 skip-silu ≠ S50 half-swap ≠ S56 input-negate |
| Attn scale ÷50（S68） | unique digit/`1.1.1…` 混杂；identical-mode 低估 | **`token_repeat`** | **L2**（attn temp too cold）；≠ S34 scale→1.0 ≠ S49 scale×50 |
| Embed negate（S69，`mul_(-1)` after lookup） | 全请求 `!!!!…`；**logits non-finite** | **`logits_finite` 为主** | **L2**（wrong embed polarity）；≠ S43 embed×100 |
| Variance eps ×1000（S70，eps into add-RMSNorm） | digit/`1.1.1…` 复读混杂 | **`token_repeat`** | **L2**（wrong norm eps）；≠ S26 fp32-mul ≠ S38 skip ≠ S66 weight-negate |
| RMSNorm weight ×50（S71） | 全请求 `!!!!…`；**logits non-finite** | **`logits_finite` 为主** | **L2**（wrong norm-weight mag）；≠ S66 weight-negate |
| SwiGLU out ×50（S72，`out*=50` after npu_swiglu） | 全请求 `!!!!…`；**logits non-finite** | **`logits_finite` 为主** | **L2**（wrong SwiGLU out mag）；≠ S39 skip ≠ S50 swap ≠ S56 in-neg ≠ S67 out-neg |
| RMSNorm x negate（S73，`x=-x` before add-RMSNorm） | 全请求 `!!!!…`；**logits non-finite** | **`logits_finite` 为主** | **L2**（wrong pre-norm act polarity）；≠ S48 residual-neg ≠ S62 pre-norm×50 |
| RMSNorm weight ÷50（S74） | 短语/`numpy` 复读塌缩 | **`token_repeat`** | **L2**（wrong norm-weight mag low）；≠ S66 negate ≠ S71 ×50 |
| Hidden ÷50 before lm-head（S75） | digit/`1.1.1…` 复读 | **`token_repeat`** | **L2**（wrong pre-head hidden mag low）；≠ S61 ×50 ≠ S53 logits÷50 ≠ S65 logits×50 |
| SwiGLU input ×50（S76，`x*=50` before npu_swiglu） | 全请求 `!!!!…`；**logits non-finite** | **`logits_finite` 为主** | **L2**（wrong SwiGLU input mag）；≠ S39/S50/S56/S67/S72 |
| Variance eps ÷1000（S77） | digit/`1.1.1…` 复读混杂 | **`token_repeat`** | **L2**（wrong norm eps low）；≠ S70 eps×1000 |
| RMSNorm x ÷50（S78，`x/=50` before add-RMSNorm） | 换行/`sentence` 复读塌缩 | **`token_repeat`** | **L2**（wrong pre-norm act mag low）；≠ S62 ×50 ≠ S73 x-negate |
| Cos/sin ×50 into RoPE（S79） | digit/`10.10…` + Nile phrase 混杂 | **`token_repeat`** | **L2**（wrong rope phase mag）；≠ S37 pos-zero ≠ S40 skip ≠ S42 phase-neg ≠ S25/S28 |
| Embed ÷50（S80） | 短句/换行复读；detect 可 <n_req | **`token_repeat`** | **L2**（wrong embed mag low）；≠ S43 ×100 ≠ S69 negate |
| SwiGLU input ÷50（S81，`x/=50` before npu_swiglu） | 短语/`swer` 复读塌缩 | **`token_repeat`** | **L2**（wrong SwiGLU input mag low）；≠ S39/S50/S56 ≠ S76 ×50 |
| Cos/sin ÷50 into RoPE（S82） | `,`/`and the` 复读混杂 | **`token_repeat`** | **L2**（wrong rope phase mag low）；≠ S37/S40/S42 ≠ S79 ×50 |
| Attn-out ×50 after FA（S83） | `...`/换行复读塌缩 | **`token_repeat`** | **L2**（wrong attn-out mag mild）；≠ S41 ×1000（常 `logits_finite`）≠ S63 negate |
| Positions ÷2 before RoPE（S84，floor-div） | `. . .` 空格复读混杂 | **`token_repeat`** | **L2**（wrong pos mag low）；≠ S37 pos-zero ≠ S57 ×2 |
| Temp ÷50（S85，post-temp logits×50） | digit/`1.1.1…` 复读；需 T>0 | **`token_repeat`** | **L2**（wrong T scale low）；≠ S36 post-temp÷50（T×50） |
| RMSNorm-out negate（S86，`-x` after add-RMSNorm） | 全请求 `!!!!…`；**logits non-finite** | **`logits_finite` 为主** | **L2**（wrong post-norm polarity）；≠ S73 pre-norm x-neg ≠ S66 weight-neg |
| RMSNorm-out ×50（S87，`x*=50` after add-RMSNorm） | 全请求 `!!!!…`；**logits non-finite** | **`logits_finite` 为主** | **L2**（wrong post-norm mag）；≠ S62 pre-norm×50 ≠ S86 out-negate |
| Residual-post negate（S88，`-residual` after add-RMSNorm） | 全请求 `!!!!…`；**logits non-finite** | **`logits_finite` 为主** | **L2**（wrong post-residual polarity）；≠ S48 pre-residual-neg ≠ S86 out-neg |
| RMSNorm-out ÷50（S89，`x/=50` after add-RMSNorm） | 短语/`numpy` 复读塌缩 | **`token_repeat`** | **L2**（wrong post-norm mag low）；≠ S87 ×50 ≠ S78 pre-norm÷50 |
| Residual-post ×50（S90，`residual*=50` after add-RMSNorm） | 全请求 `!!!!…`；**logits non-finite** | **`logits_finite` 为主** | **L2**（wrong post-residual mag）；≠ S55 pre× ≠ S64 pre÷ ≠ S88 post-neg |
| Residual-post ÷50（S91，`residual/=50` after add-RMSNorm） | `[code` 短语复读塌缩 | **`token_repeat`** | **L2**（wrong post-residual mag low）；≠ S90 post× ≠ S64 pre÷ ≠ S88 negate |
| Temp-skip（S92，skip `apply_temperature`） | unique rambling；**identical precision=0**；需 T>0 | **`token_repeat`** | **L2**（requested T ignored）；≠ S36 post÷50 ≠ S85 post×50；**detect≈n_req 仍 PASS**（勿因 precision=0 判 GAP） |
| Residual←normed-x（S93，`return x,x` after add-RMSNorm） | `[it` 短语复读塌缩 | **`token_repeat`** | **L2**（wrong residual wiring：residual=normed x）；≠ S31 drop ≠ S94 swap ≠ S88–S91 post-residual mag/polarity |
| Residual↔x swap（S94，`return residual,x` after add-RMSNorm） | 全请求 `!!!!…`；**logits non-finite** | **`logits_finite` 为主** | **L2**（wrong stream wiring：tuple swap）；≠ S31 drop ≠ S93 residual←x ≠ S88 post-neg |
| Temp-double（S95，`apply_temperature`×2） | 低 precision identical + per-req detect；需 T>0 | **`token_repeat`** | **L2**（T applied twice → colder）；≠ S36 post÷50 ≠ S85 post×50 ≠ S92 skip |
| RMSNorm-weight=ones（S96，`ones_like(weight)` into add-RMSNorm） | unique dynled；**identical precision=0**；detect 可 <n_req | **`token_repeat`** | **L2**（identity norm weight）；≠ S66 weight-neg ≠ S71 ×50 ≠ S74 ÷50；**detect>0 仍 PASS**（勿因 precision=0 判 GAP） |
| Residual-leak-add（S97，`x=x+residual` after add-RMSNorm） | 全请求 `!!!!…`；**logits non-finite** | **`logits_finite` 为主** | **L2**（post-norm residual leak）；≠ S31 drop ≠ S93 residual←x ≠ S94 swap ≠ S88–S91 |
| Min_p-skip（S98，skip `apply_min_p`） | unique rambling；**identical precision=0**；需 T>0 + min_p | **`token_repeat`** | **L2**（requested min_p ignored）；≠ S36/S85/S92/S95 temp class ≠ S46 penalty；**detect≈n_req 仍 PASS** |
| Top_p-skip（S99，skip `apply_top_k_top_p`） | unique rambling；**identical precision=0**；需 T>0 + top_p | **`token_repeat`** | **L2**（requested nucleus/k ignored）；≠ S45 topk-on-neg（FAIL+GAP）≠ S98 min_p-skip ≠ temp class；**detect≈n_req 仍 PASS** |
| RMSNorm-bias=weight（S100，`bias=weight` into add-RMSNorm） | identical 异地×N 复读 | **`token_repeat`** | **L2**（wrong norm bias wiring）；≠ S66/S71/S74 weight mag/sign ≠ S96 ones |
| Cos/sin-half-swap（S101，swap halves of RoPE cos_sin_cache） | identical `111…` 复读 | **`token_repeat`** | **L2**（wrong rope phase halves）；≠ S42 negate ≠ S79–S82 scale ≠ S40 skip ≠ S25/S28 |
| RMSNorm-out-abs（S102，`x=abs(x)` after add-RMSNorm） | 混杂英文/`pl` 复读 | **`token_repeat`** | **L2**（destroy signed post-norm act）；≠ S86 out-neg ≠ S87–S89 out mag |
| SwiGLU-gate-only（S103，`silu(gate)` drop up-mul） | unique garbage；**identical precision=0** | **`token_repeat`** | **L2**（incomplete SwiGLU：gate only）；≠ S39 skip-silu ≠ S50 half-swap ≠ S56–S81；**detect≈n_req 仍 PASS** |
| Rope-skip-key（S104，rotate Q only；K unrotated） | identical `One. One.…` 复读 | **`token_repeat`** | **L2**（Q/K RoPE phase mismatch）；≠ S40 full-skip ≠ S25/S28 ≠ S101 half-swap |
| Rope-skip-query（S105，rotate K only；Q unrotated） | phrase-repeat 垃圾 | **`token_repeat`** | **L2**（Q/K RoPE phase mismatch，对偶于 S104）；≠ S104 skip-K ≠ S40/S25/S28/S101 |
| Residual-post-abs（S106，`residual=abs(residual)` after add-RMSNorm） | 混杂 servlet 复读；precision 可 <n_req | **`token_repeat`** | **L2**（unsigned post-residual）；≠ S88 post-neg ≠ S90–S91 mag ≠ S102 out-abs |
| SwiGLU-up-only（S107，return up half；drop silu(gate)*up） | identical 短语复读 | **`token_repeat`** | **L2**（incomplete SwiGLU：up only）；≠ S103 gate-only ≠ S39 skip-silu ≠ S50 half-swap |
| Hidden-abs（S108，`hidden=abs(hidden)` before lm-head） | 混杂 cyrillic/`индив` 复读 | **`token_repeat`** | **L2**（unsigned pre-head hidden）；≠ S61 hidden×50 ≠ S75 hidden÷50 |
| Value-abs（S109，`value=abs(value)` before FA） | unique garbage；**identical precision=0**；detect 可 <n_req | **`token_repeat`** | **L2**（unsigned V）；≠ S58 value-neg ≠ S51 value×；**detect>0 仍 PASS**（勿因 precision=0 判 GAP） |
| RMSNorm-weight-abs（S110，`abs(weight)` into add-RMSNorm） | digit/`1.1.1…` 复读；precision 可 <n_req | **`token_repeat`** | **L2**（unsigned norm weight）；≠ S66 neg ≠ S71 ×50 ≠ S74 ÷50 ≠ S96 ones ≠ S100 bias=weight |
| Key-abs（S111，`key=abs(key)` before FA） | 空格/`,` 复读混杂；precision 可 <n_req | **`token_repeat`** | **L2**（unsigned K）；≠ S54 key-neg ≠ S59 key× ≠ S109 value-abs |
| Embed-abs（S112，`embedding.abs_()` after lookup） | 换行塌缩；detect 可 <n_req | **`token_repeat`** | **L2**（unsigned embed）；≠ S69 embed-neg ≠ S43 ×100 ≠ S80 ÷50 |
| Cos/sin-abs（S113，`abs(cos_sin_cache)` into RoPE） | unique-ish Nile 散文；**identical precision=0** | **`token_repeat`** | **L2**（unsigned rope phase）；≠ S42 negate ≠ S79–S82 scale ≠ S101 half-swap ≠ S40 skip；**detect≈n_req 仍 PASS** |
| Query-abs（S114，`query=abs(query)` before FA） | `for`/`one of` 复读；completes Q/K/V abs | **`token_repeat`** | **L2**（unsigned Q）；≠ S52 query-neg ≠ S60 query× ≠ S109 value-abs ≠ S111 key-abs |
| SwiGLU-out-abs（S115，`out=abs(out)` after npu_swiglu） | 中文/换行复读混杂；precision 可 <n_req | **`token_repeat`** | **L2**（unsigned SwiGLU out）；≠ S67 out-neg ≠ S72 out× ≠ S103 gate-only ≠ S107 up-only |
| RMSNorm-x-abs（S116，`x=abs(x)` before add-RMSNorm） | identical `pl` 复读 | **`token_repeat`** | **L2**（unsigned pre-norm x）；≠ S73 x-neg ≠ S62 ×50 ≠ S78 ÷50 ≠ S102 out-abs |
| Query-scale-down（S117，`query/=50` before FA） | digit/`1.1.1…` 复读；precision 可 <n_req | **`token_repeat`** | **L2**（wrong Q magnitude low）；≠ S60 query×50 ≠ S52 query-neg ≠ S114 query-abs |
| Key-scale-down（S118，`key/=50` before FA） | digit/`1.1.1…` 复读；precision 可 <n_req | **`token_repeat`** | **L2**（wrong K magnitude low）；≠ S59 key×50 ≠ S54 key-neg ≠ S111 key-abs |
| Residual-pre-abs（S119，`residual=abs(residual)` before add-RMSNorm） | 混杂 servlet/mixed-script 复读；precision 可 <n_req | **`token_repeat`** | **L2**（unsigned pre-residual）；≠ S48 pre-neg ≠ S55/S64 mag ≠ S106 post-abs |
| RMSNorm-weight=zeros（S120，`zeros_like(weight)` into add-RMSNorm） | 全请求 `!!!!…` 塌缩 | **`token_repeat`** | **L2**（collapsed norm weight）；≠ S96 ones ≠ S66 neg ≠ S71 ×50 ≠ S74 ÷50 ≠ S110 abs |
| SwiGLU-input-abs（S121，`x=abs(x)` before npu_swiglu） | unique mixed-script garbage；**identical precision=0** | **`token_repeat`** | **L2**（unsigned SwiGLU input）；≠ S56 input-neg ≠ S76 ×50 ≠ S81 ÷50 ≠ S115 out-abs；**detect≈n_req 仍 PASS**（勿因 precision=0 判 GAP） |
| Logits-abs（S122，`logits.abs()` after lm-head） | digit/`1.1.1…` 复读；precision 可 <n_req | **`token_repeat`** | **L2**（unsigned logits）；≠ S53 logits÷50 ≠ S65 logits×50 ≠ S108 hidden-abs |
| RMSNorm-bias=-weight（S123，`bias=-weight` into add-RMSNorm） | `.ON.ON…` 短语复读；precision 可 <n_req | **`token_repeat`** | **L2**（wrong norm bias polarity）；≠ S100 bias=+weight ≠ S66 weight-neg ≠ S120 weight-zeros |
| Penalty-skip（S124，skip `apply_penalties`） | unique id-echo / Nile 散文；**identical precision=0**；需 T>0 | **`token_repeat`** | **L2**（ignored penalties）；≠ S46 sign-flip ≠ S98 min_p-skip ≠ S99 top_p-skip；**detect≈n_req 仍 PASS**（勿因 precision=0 判 GAP） |
| Residual-leak-sub（S125，`x=x-residual` after add-RMSNorm） | 全请求 `!!!!…`；**logits non-finite** | **`logits_finite` 为主** | **L2**（wrong residual recombine：sub）；≠ S97 leak-add ≠ S93 residual←x ≠ S94 swap ≠ S31 drop |
| Hidden-zeros（S126，`hidden.zero_()` before lm-head） | 全请求 `!!!!…` 塌缩 | **`token_repeat`** | **L2**（collapsed pre-head hidden）；≠ S61 ×50 ≠ S75 ÷50 ≠ S108 abs ≠ S122 logits-abs |
| Embed-zeros（S127，`embedding.zero_()` after lookup） | 全请求 `!!!!…` 塌缩 | **`token_repeat`** | **L2**（collapsed embed）；≠ S69 neg ≠ S43 ×100 ≠ S80 ÷50 ≠ S112 abs |
| Cos/sin-zeros（S128，`zeros_like(cos_sin_cache)` into RoPE） | `,`/`and the` 短语复读；precision 可 <n_req | **`token_repeat`** | **L2**（collapsed rope phase）；≠ S42 neg ≠ S79–S82 scale ≠ S101 half-swap ≠ S113 abs |
| Residual-pre-zeros（S129，`residual.zero_()` before add-RMSNorm） | identical `FieldType` 短语复读 | **`token_repeat`** | **L2**（collapsed pre-residual）；≠ S48 neg ≠ S55/S64 mag ≠ S119 abs ≠ S31 drop |
| Query-zeros（S130，`query.zero_()` before FA） | `,`/`and the` 短语复读；precision 可 <n_req | **`token_repeat`** | **L2**（collapsed Q）；≠ S60 ×50 ≠ S52 neg ≠ S114 abs ≠ S117 ÷50 |
| SwiGLU-out-zeros（S131，`out.zero_()` after npu_swiglu） | `...` 换行复读 | **`token_repeat`** | **L2**（collapsed SwiGLU out）；≠ S67 neg ≠ S72 ×50 ≠ S115 abs ≠ S103 gate-only ≠ S107 up-only |
| Key-zeros（S132，`key.zero_()` before FA） | `,`/`and the` 短语复读；precision 可 <n_req | **`token_repeat`** | **L2**（collapsed K）；≠ S54 neg ≠ S59 ×50 ≠ S111 abs ≠ S118 ÷50 |
| SwiGLU-input-zeros（S133，`x.zero_()` before npu_swiglu） | `...` 换行复读 | **`token_repeat`** | **L2**（collapsed SwiGLU input）；≠ S56 neg ≠ S76 ×50 ≠ S81 ÷50 ≠ S121 abs ≠ S131 out-zeros |
| Cos/sin-ones（S134，`ones_like(cos_sin_cache)` into RoPE） | Nile/`river` 短语复读 | **`token_repeat`** | **L2**（unit rope phase）；≠ S42 neg ≠ S79–S82 scale ≠ S101 half-swap ≠ S113 abs ≠ S128 zeros |
| Residual-post-zeros（S135，`residual.zero_()` after add-RMSNorm） | identical `FieldType` 短语复读 | **`token_repeat`** | **L2**（collapsed post-residual）；≠ S88 post-neg ≠ S90/S91 mag ≠ S106 post-abs ≠ S129 pre-zeros |
| RMSNorm-out-zeros（S136，`x.zero_()` after add-RMSNorm） | 全请求 `!!!!…` 塌缩 | **`token_repeat`** | **L2**（collapsed post-norm x）；≠ S86 out-neg ≠ S87 out× ≠ S89 out÷ ≠ S102 out-abs |
| Embed-ones（S137，`ones_like(embedding)` after lookup） | identical `××…` 复读 | **`token_repeat`** | **L2**（unit embed）；≠ S69 neg ≠ S43 ×100 ≠ S80 ÷50 ≠ S112 abs ≠ S127 zeros |
| Hidden-ones（S138，`ones_like(hidden)` before lm-head） | identical `pl` 复读 | **`token_repeat`** | **L2**（unit pre-head hidden）；≠ S61 ×50 ≠ S75 ÷50 ≠ S108 abs ≠ S126 zeros |
| Positions-ones（S139，`ones_like(positions)` before update_cos_sin） | digit/`Friday` 复读；precision 可 <n_req | **`token_repeat`** | **L2**（pos collapse to 1）；≠ S37 pos→0 ≠ S57 ×2 ≠ S84 ÷2 |
| Residual-pre-ones（S140，`ones_like(residual)` before add-RMSNorm） | identical `[code` 短语复读 | **`token_repeat`** | **L2**（unit pre-residual）；≠ S48 neg ≠ S55/S64 mag ≠ S119 abs ≠ S129 zeros |
| Query-ones（S141，`ones_like(query)` before FA） | `,`/`one of`/空格复读；precision 可 <n_req | **`token_repeat`** | **L2**（unit Q）；≠ S60 ×50 ≠ S52 neg ≠ S114 abs ≠ S117 ÷50 ≠ S130 zeros |
| Key-ones（S142，`ones_like(key)` before FA） | `,`/`and the` 短语复读；precision 可 <n_req | **`token_repeat`** | **L2**（unit K）；≠ S54 neg ≠ S59 ×50 ≠ S111 abs ≠ S118 ÷50 ≠ S132 zeros |
| SwiGLU-out-ones（S143，`ones_like(out)` after npu_swiglu） | identical `造假` 短语复读 | **`token_repeat`** | **L2**（unit SwiGLU out）；≠ S67 neg ≠ S72 ×50 ≠ S115 abs ≠ S131 zeros |
| Residual-post-ones（S144，`ones_like(residual)` after add-RMSNorm） | identical `[code` 短语复读 | **`token_repeat`** | **L2**（unit post-residual）；≠ S88 post-neg ≠ S90/S91 mag ≠ S106 post-abs ≠ S135 zeros |
| RMSNorm-out-ones（S145，`ones_like(x)` after add-RMSNorm） | identical `pl` 复读 | **`token_repeat`** | **L2**（unit post-norm x）；≠ S86 out-neg ≠ S87 out× ≠ S89 out÷ ≠ S102 out-abs ≠ S136 zeros |
| SwiGLU-input-ones（S146，`ones_like(x)` before npu_swiglu） | identical `造假` 短语复读 | **`token_repeat`** | **L2**（unit SwiGLU input）；≠ S56 neg ≠ S76 ×50 ≠ S81 ÷50 ≠ S121 abs ≠ S133 zeros |
| Positions-zeros（S147，`zeros_like(positions)` before update_cos_sin） | digit/`\`` 复读；detect 可 <n_req | **`token_repeat`** | **L2**（pos collapse to 0）；≠ S139 ones ≠ S57 ×2 ≠ S84 ÷2 |
| Value-ones（S148，`ones_like(value)` before FA） | identical `ior` 短语复读；precision 可 <n_req | **`token_repeat`** | **L2**（unit V）；≠ S58 neg ≠ S51 ×50 ≠ S109 abs |
| Attn-out-ones（S149，`ones_like(attn_output)` after FA） | identical `ior` 短语复读；precision 可 <n_req | **`token_repeat`** | **L2**（unit attn-out）；≠ S63 neg ≠ S41 ×1000 ≠ S83 ×50 |
| RMSNorm-x-ones（S150，`ones_like(x)` before add-RMSNorm） | identical `pl` 复读 | **`token_repeat`** | **L2**（unit pre-norm x）；≠ S73 x-neg ≠ S62 x× ≠ S78 x÷ ≠ S116 x-abs |
| Logits-ones（S151，`ones_like(logits)` after lm-head） | identical `!!!!` / token0 塌缩 | **`token_repeat`** | **L2**（unit logits）；≠ S122 abs ≠ S53 ÷50 ≠ S65 ×50；≠ S44 zero_ INVALID |
| RMSNorm-bias-zeros（S152，`zeros_like(weight)` as bias into add-RMSNorm） | digit/`1.0.0…` 复读；precision 可 <n_req | **`token_repeat`** | **L2**（zero bias inject）；≠ S100 bias=weight ≠ S123 bias=-weight ≠ S96 weight=ones |
| RoPE 第二半写丢（S25，soft-inv #7082） | digit/`1.1.1…` 复读塌缩 | **`token_repeat`** | **L2 class-hint**（RoPE half）；≠ S11 pad；勿宣称定位到 Triton store 行 |
| RMSNorm fp32 weight-mul（S26，soft-inv #42379） | 同上类复读；dtype/cast | **`token_repeat`** | **L2**（norm dtype）；与 S25 症状可重叠，靠 overlay/场景区分 |
| RoPE neox→interleaved 风格错（S28，#7341/#7082 class） | 句/短语级复读（score=`phrase_repeat`） | **`token_repeat`** | **L2**；≠ S25 half-drop ≠ S11；samples 可能看似「正常英文」 |
| Softcap / 不稳定 softmax 数值溢出（S20，constructed） | 全请求 `!!!!…` / token0 塌缩；temp≪1 放大 | **`token_repeat` 为主**；兼开 `logits_finite` | Inf/NaN 可能在采样内被吃掉 → 未必亮 `logits_finite`；MRV2 须打 **V2 Sampler**（非仅 AscendTopKTopPSampler） |
| Logits fp16 demote（S29，sampling/cast） | digit/`1.1.1…` 复读；低 temp 放大 | **`token_repeat`** | **L2**（cast）；≠ S20 softcap ≠ S26 RMSNorm mul；打 **V2 Sampler** |
| Null-block KV dirt（S30，soft-inv #39444） | 复读塌缩；block0 脏 | **`token_repeat`** | **L2**（+可选 L3 KV）；≠ S01 skip-zero ≠ S10 recycle ≠ S23/S24 |
| Residual stream drop（S31） | 强 identical 短语复读（如 `FieldType`×N） | **`token_repeat`** | **L2**（add-rms 丢 residual）；≠ S26（fp32-mul 仍 accumulate） |
| Spec residual resample RNG 无 SALT（S22，#18657） | 接受率异常偏低（如 0–0.27）；文本可看似正常 | **`spec_acceptance` 为主**；辅 `token_repeat` | ≠ S05（NaN argmax）；≠ S20；需 MTP/eagle3 + `temperature>0`；precision 常为 **分布性**（勿只靠 samples 垃圾启发式） |
| 权重腐蚀 always-on（S23，constructed） | 启动后恒定复读/塌缩 | **`token_repeat`** | **仅 L1 detect**；禁止宣称哪一层/哪个 weight；负对照=干净 ckpt |
| 量化 scale always-on（S24，constructed） | W8A8 启动后恒定 `token_repeat` | **`token_repeat`** | **仅 L1**；≠ S07（路径触发+GAP）；**不能**指出哪条 scale |
| 有限垃圾 / 跨请求全同 / unique garbage（S07,S45；**不含** dense-S01） | mixed-script、identical、或 per-req unique garbled | **当前均弱** | **GAP**（S07/S45）：见 `DETECTOR_GAPS.md`。**S01** dense 复判为 **FAIL（复现未出现）**（precision CJK 误标；patch 入口未切满量时 trigger 可 0）——勿再当 GAP |
| NaN/Inf 数值炸（logits 仍可见） | non-finite logits | `logits_finite` | 有限垃圾 **不会** 命中；与 S20 塌缩路径区分 |

有限垃圾 / identical-across-requests：**不要**宣称「未复现」；归档 samples + `score_completion_samples`，标 **GAP**，等未来 garbled / cross-req detector。

## Step 2 — 委派（禁止自创配置参数）

| 现状 | 调用 |
|------|------|
| 现象未定类 | `runtime-guard-detector-sweep` → 临时只 report |
| 现象已定类 / 要抓 dump | `runtime-guard-config-recommender`（`troubleshoot`） |
| 业务要恢复默认全关 | `config-recommender`（`business_default`） |
| 已有 report（±dump） | `runtime-guard-analysis` |
| report 空但有 completion samples / FAIL+GAP | `analysis` → `score_completion_samples`（勿 skip） |
| analysis 得 verify=PASS 且可起清洁标杆 | `runtime-guard-ref-kv-dump` |

可**复述**下游给出的 JSON；**禁止**自己编造 window / 阈值 / `auto_max_times` / cooldown / `on_trigger`。

启服与热更细节见手册 01；源码路径须含 `observability/runtime_guard/`（MRV2）。`releases/v0.30.0` / rc 线无 Guard 时先看 [05](../../05_v030_backport/README.md)（BASE 见 CHANGELOG；`v0.30-rg.3` tip 已对齐 #18644）。

## 压测抓命中（用户页 Step 3 纪律）

- 有多份 report / sample 时优先看明显错误的（乱码 / 异常样本）。  
- **先信 detector**，再用输出反查；勿因「看起来正常」直接否命中。  
- `report.save_sensitive_info: true` 才能把 token ids 留给 force-feed。

## force-feed（与 `ref-kv-dump` 对齐）

按报告里的 **token id** 原样喂给干净服务；**禁止**字符串重 tokenize。同模型 / 同拓扑 / **同 MODE**；只用 native `dump_kv`。细节与脚本见 [`ref-kv-dump`](../ref-kv-dump/SKILL.md)。

- 默认 `--feed=history` → 对比长度 **`n_prompt + n_output - 1`**（不要按 `p+o` 全长，否则末 token 假分歧）。  
- 空 `prompt_token_ids`：优先合 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) 重抓，或 re-curl；禁止 tokenize 补造。

## 目标（定界，非定位）— 十问

用户面检查单：[02 §5](../../02_problem_localization/README.md#5-kv-定界十问检查单有-buggyref-时按序)。有 buggy+ref 时按序答（对比细节在 `ref-kv-dump`）：

| 问 | 检查 outcome |
|----|--------------|
| **Q1** | KV 是否异常？（高相似无首分歧 → 非 KV，停） |
| **Q2** | 首个不一致在 **prompt 还是 output**？索引大概在哪？ |
| **Q3** | 层：全层齐坏，还是 **从某层起坏**？ |
| **Q4** | 粒度：单 token / 连续 / 是否按 **`block_size`** 对齐？ |
| **Q5** | 首分歧之后 **是否恢复**（邻域 ~1 vs 一路坏）？ |
| **Q6** | **output 首 token 余弦**是否已明显偏低？（无 output 答未知） |
| **Q7** | cos **形态**：断崖→0 / 平台 ~0.8–0.9 / nan·inf？ |
| **Q8** | 是否 **仅 PD** 复现？单 P、单 D 各如何？（非 PD 答不适用/未测） |
| **Q9** | **和哪些特性相关 / 不相关**？（已做消融结果） |
| **Q10** | **对照是否完整可用**？（对比窗含 output？last-PP 各 TP 齐？同 MODE/同拓扑？） |

### 写作纪律（何时再推断 / 禁止）

- **正文必写的 KV 事实**（再推断）：首不一致在 prompt 还是 output；后续是否恢复；output 首 token 余弦；是否仅 PD 复现。  
- **何时再推断：** 上述事实写清后，再推「何时脏 / 是否传写交接」。  
- **禁止：** 从坏输出直接跳根因；把 overlay / 上游 PR 已知根因写成定界已证。  
- **空 `prompt_token_ids`：** 不等于「十问不适用」；同 prompt re-curl 抓实际 ids 后仍可做 KV 排除定界。包内未跑对比写「尚未做 KV 对比…」，勿编造未跑数字。  
- **logits_finite 命中：** 仍做 KV：有效槽 Inf/NaN、未用槽（有限非 0=记卫生/脏写，Inf/NaN=可影响结果）、（有限时）十问/③/④。全 NaN cos **不定层**，但「有效槽已非有限」本身是事实。勿跳过 KV；msprobe 仅在 KV 分流后需要算子首坏时再开。

### 定界写作标准（事实 → 推断 → 结论）

1. **事实** — 包内可核对项：现象、三层、report/detector、`prompt_token_ids` 是否空、是否 re-curl、KV 对比是否归档（未做写明；已做写实数）。  
2. **推断** — 只写事实支撑得住的允许/排除；不够就写推不出什么。  
3. **结论** — 写清已定界到 / 尚未定界到；定界不出写「分析不出 / 证据不足」。

**统一定界禁例（案例教学禁写并入此处）：** 不可写「坏输出 → 所以进错专家 / MoE topk / K/V 对调 / gate-up 对调」等；构造根因只放「案例背景/构造」，不放进定界推断。案例页只留 outcome/事实，不写教学禁例段。

### keep-set 结案四档（主标签；≠ PASS/FAIL/GAP）

案例 **headline 结案**只用四档（详见 [04](../../04_case_studies/README.md)）。PASS/FAIL/GAP 仅作 **detector / verify 侧**用语，不作整案总评。

| 档 | 何时 |
|----|------|
| **未复现** | 目标异常形态未出现（通顺输出 ≠ 目标乱码；有 trigger 也不够） |
| **复现未抓到** | 异常已现/应现，但**无有效异常 KV** 可对账（含 `logits_finite`：有 report 却未落/未保留可检 dump） |
| **KV 一致→排除 KV** | 有效对账且匹配（有效槽有限且余弦匹配；未用槽有限非 0 可附注卫生问题，**不**单凭此否决「排除」） |
| **KV 不一致→定界** | 有效对账且不匹配 → 按十问写事实摘要；**有效槽 Inf/NaN** 或 **未用槽 Inf/NaN** 为严重数值信号（勿用 NaN cos 伪层名）；未用槽仅有限非 0 → 记脏写，通常不单独定「结果由此坏」 |

**`logits_finite`：** 与 `token_repeat` 一样进 KV 路径；检测写「检出」；结案按上表③/④（或确无 dump 才②）。**msprobe 不是结案档替代**，是 KV 后的可选算子探针。

**检测（辅）** 另写：三层或「检出 / 漏检 / …漏检」。mere **detect=0** 不自动等于「复现未抓到」——若 `manual_dump` 已抓到有效异常 KV 并完成对账，按③/④。

### 证据完整性（踩坑硬纪律）

1. **钉点同跑** — detect 钉点、KV dump、`kv_compare`、定界结论必须来自**同一次异常请求**（同 `req_id` / 同 wave）。禁止把 A 跑的 report 与 B 跑的 dump / 旧 `kv_compare` 拼成一案。  
2. **有效异常 KV 前提** — 未复现、非目标形态、或**弱 dump**（如仅 o=1 / 窗过短 / 非异常样本）→ **不得**写成已做有效对账；写「未复现 → 无有效异常 KV → 未做有效对账」或留空档 **复现未抓到**。  
3. **数值问题 / 无有效余弦 ≠ 定位** — 格点标 **数值问题** 或 per-token 无干净 cos 时，**禁止**把旧脚本 NaN 排序伪出的 `first_mismatch_idx` / 层名写成「token0@layer_L」；有效槽全非有限只记该事实。有干净格再写余弦首分歧（细则见 `ref-kv-dump`）。  
4. **无证据留空** — 不可信混档 / 清空实测后：删 samples/reports/三层/跑批/`kv_compare`，结案与定界**留空**；勿保留半截旧结论或编造数字。  
5. **多组验证** — 写③/④前至少再跑一组（同 overlay、独立请求）确认 cos 结论同向；单次弱窗不作定论。  
6. **`kv_cache` 生命周期** — **抓前清空**本轮工作目录（防旧 dump 混入）；**对账中保留**本轮产物；归档后再清。细则见 `ref-kv-dump`。  
7. **KV 对比：先形状、数值门闩、只比有效 token** — dump 是整 block；未用槽常为 0；history feed 用 `p+o-1`。(token,layer) 有 NaN/Inf/零范数 → **数值问题**（不算 cos）。勿按全容量或错跨度算 cos（虚高/末位假分歧）。  
8. **压测时限** — 单场景最长约 **1h**；超时未复现 → **未复现**（附 knobs/负载），勿空耗或放大器硬凑。  
9. **`logits_finite` → 仍先 KV，msprobe 殿后** — 先判必现（并问他环境是否正常）；抓 buggy+清洁/跨环境标杆（标杆未炸；跨环境须权重 MD5 + 代码 commit 一致）。检查顺序：有效槽有限/Inf/NaN → 未用槽分级 → 逐格数值门闩 →（干净格）shape + `p+o-1` 余弦。**禁止**把数值问题/NaN cos 写成层定界；**禁止**因 logits 命中就跳过 KV。需要算子首坏时再开 [`msprobe-dump`](../msprobe-dump/SKILL.md)（`task=statistics`，**`--enforce-eager`**，禁图；全程挂钩、开销大）。  
10. **跨环境标杆** — 必现且存在正常环境时可用；**禁止**在权重/代码未对齐时把他环境 dump 当 ref（细则 `ref-kv-dump`）。

### KV/余弦时机方法示例（示意数字，非某包实测）

交叉对照 [`ref-kv-dump`](../ref-kv-dump/SKILL.md) 信号表。

| 要写清的事实 | 为何要写 |
|--------------|----------|
| 首个不一致在 **prompt** 还是 **output** | prefill 段脏 vs decode 才脏 |
| 其后是否恢复 ~1 | 写入后污染/串槽 vs 持续错源 |
| **output 首 token** 余弦是否已低 | decode 开跑前状态是否已坏 |
| 是否 **仅 PD** 复现 | 收窄传写/交接 |

示意链：首不一致 idx=5 仍在 prompt → 其后多槽又回 ~1 → out0 cos 已低（~0.8）→ 仅 PD 复现 → 推「prefill 进行到一定进度后、decode 前」脏；**禁止**从坏输出跳「进错专家」。

### 交付模板（定界）

能定到哪写到哪；未知填「未知」；**勿每次固定声明**「未定位算子/提交」。无标杆：标杆=无，停在「问题类 + 可归档现场」；**不要伪造 ref**。

```text
【定界】KV=<异常|正常|未知(无标杆)>; 阶段=<prefill|decode|未知>;
首坏token=<i/role|未知>; 首坏层=<L|未知>;
粒度=<单token|连续|block|未知>; 时机=<写入时即坏|写入后污染|未知>;
类型=<污染断崖|计算平台|后采样/非KV|仅detector类>;
标杆=<有|无>; 证据=<report路径 / dump路径 / 脚本>;
```

### 复现错跑提醒（S25/S26/S33 族）

**现行：** 英文河名短句 `Name one famous river… id={i}.` × **48 并发** + `token_repeat` 阈值 **8**。  
**历史错跑：** 「中文回声式」prompt + 约 8 条串行 + 阈值 16 → 常无 `1.1.1…`、detect=0 → **复现条件不对，不是漏检**。  
S45：勿用伪造 NaN/填 token / amplifier-retune 刷成 PASS；有异常+detect=0 记 FAIL+GAP。

## forbidden

- 在本 skill 内手写完整排障 JSON / 离线脚本流程 / force-feed 实现  
- 承诺定位算子、内核或具体 commit  
- 从本流程跳过 `verify_request_kv` 直接宣称可做层定界  
- 把「十问不适用」写进空 prompt 案例结案  
- 混用不同 run 的 report/dump/`kv_compare`；用全 NaN / 弱 dump 伪写层定位  
- 用 PASS/FAIL/GAP 当 keep-set 案例 headline 结案  
- 未清 `kv_cache` 就开新抓；跳过 shape、把 block 未用 0 槽算进相似度  
- 跨环境未核权重 MD5 / 代码 commit 就当干净标杆  
- history feed 下按 `p+o` 全长比出的**仅末 token**分歧写成③/④或层定位；tokenize 补造 prompt ids

## Related

`detector-sweep` · `config-recommender` · `analysis` · `ref-kv-dump` · `msprobe-dump` · [SKILLS_METADATA.md](./SKILLS_METADATA.md)
