---
name: runtime-guard-investigation
description: >-
  Orchestrate end-to-end runtime_guard debugging: triage whether Guard fits,
  collect inputs, delegate to detector-sweep / config-recommender / analysis /
  ref-kv-dump, then deliver Q1–Q5 delimitation (not root-cause). Do not invent
  runtime_config thresholds or reimplement offline/ref scripts. Native dump_kv
  only; no msprobe. Align with handbook 02.
---

# runtime_guard investigation（编排总控）

**类型：编排。** 只做 triage、收集输入、委派原子 skill、汇总定界交付。  
底层配置 / 读盘 / force-feed / KV 对比 **委派**，不在本 skill 重写一遍。

手册：[02](https://github.com/djh95/runtime-guard-docs/blob/main/02_problem_localization.md) · [01](https://github.com/djh95/runtime-guard-docs/blob/main/01_enable_and_start.md) · [03](https://github.com/djh95/runtime-guard-docs/blob/main/03_detectors/README.md)  
契约：[SKILLS_METADATA.md](./SKILLS_METADATA.md)  
脚本仓：[runtime-guard-test](https://github.com/djh95/runtime-guard-test)  
产品：`vllm_ascend/observability/runtime_guard/`（[#16849](https://github.com/vllm-project/vllm-ascend/pull/16849)/[#18644](https://github.com/vllm-project/vllm-ascend/pull/18644)）

**Dump 只有 native `dump_kv`。** 禁止 msprobe / PrecisionDebugger / 自造 dumper。

## 开场必问

1. **运行环境**：容器 / 路径 / `{MODE}` / `{MODEL}` / `{TOPO}` / 卡号  
2. **启动脚本** `{START}` · **请求脚本** `{REPRO}`  
3. **谁跑服务**（确认前不要擅自起服）  
4. **版本**、能否压测、有无清洁标杆、本地是否已有 `report`/`kv_cache`

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

**适合：** `token_repeat` / `logits_finite` / `spec_acceptance`（MTP）；KV 可疑靠 dump+标杆。  
**勿启用未合入：** `output_substring` / `token_logprob` / `slot_*` / `kv_state`。

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
| Top-k/top-p on `-logits`（S45，bottom nucleus） | **unique** mixed-script garbage；identical-mode 低估 | **当前均弱** | **FAIL+GAP**（同 S01/S07）；`token_repeat`/`logits_finite` miss；勿放大器硬凑 PASS |
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
| 有限垃圾 / 跨请求全同 / unique garbage（S01,S07,S45） | mixed-script、identical、或 per-req unique garbled | **当前均弱** | **GAP**：见 `DETECTOR_GAPS.md`；S24/S46 能 detect 时勿与 S07/S45 混谈 |
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

启服与热更细节见手册 01；源码路径须含 `observability/runtime_guard/`（MRV2）。≤0.30 无 Guard 时先看 [05](https://github.com/djh95/runtime-guard-docs/blob/main/05_v030_backport/README.md)（**不含** #18644 鲁棒集合）。

## 目标（定界，非定位）

有 buggy+ref 时按序答 Q1–Q5（对比细节在 `ref-kv-dump`）：

| 问 | 要点 |
|----|------|
| Q1 KV 是否异常？ | 高相似无首分歧 → 非 KV |
| Q2 阶段/token/层？ | prefill vs decode；整包 vs 从某层起 |
| Q3 粒度？ | 单 token / 连续 / block |
| Q4 异常点之后？ | 恢复→写入后污染；一路坏→写入时即错 |
| Q5 类型（cos）？ | 断崖≈污染；平台≈计算；nan/inf≈数值炸 |

**交付模板：**

```text
【定界】KV=<异常|正常|未知(无标杆)>; 阶段=<prefill|decode|未知>;
首坏token=<i/role|未知>; 首坏层=<L|未知>;
粒度=<单token|连续|block|未知>; 时机=<写入时即坏|写入后污染|未知>;
类型=<污染断崖|计算平台|后采样/非KV|仅detector类>;
标杆=<有|无>; 证据=<report路径 / dump路径 / 脚本>;
【非结论】未定位到具体算子或提交。
```

无清洁标杆：停在「问题类 + 可归档现场」；**不要伪造 ref**。

## forbidden

- 在本 skill 内手写完整排障 JSON / 离线脚本流程 / force-feed  
- 承诺定位算子、内核或具体 commit  
- 从本流程跳过 `verify_request_kv` 直接宣称可做层定界

## Related

`detector-sweep` · `config-recommender` · `analysis` · `ref-kv-dump` · [SKILLS_METADATA.md](./SKILLS_METADATA.md)
