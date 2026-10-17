# Anomaly × Skills 能力边界（活文档）— 2026-10-17

> **用途：** 对每一个已落地 / 在册异常场景，如实记录现象、复现与对照配置、skills 能分析到哪一步、有用度，以及还缺什么。  
> **Skills：** `runtime-guard-test` `analysis/skill/` **v3.0**（investigation / detector-sweep / config-recommender / analysis / ref-kv-dump）。  
> **Guard pin：** G2 `f2aefd068`。三层率 = trigger / precision / detect。  
> **诚实上限：** skills **定界**（detect / 现象类 / 可选 KV 首分歧），**不承诺**定位到算子、权重元素或具体 commit。

**维护：** 160 builder 往 `docs/anomaly-skills-handoff.md` 塞新 PASS/FAIL+GAP → skills 方（162）补本节 + `docs/anomaly-skills-runs/`；skills 变更推 `main`。

**强制闭环：** 每次改 skills 后必须对 **同一 fail-evidence** 再跑 analyze/verify，并在 [anomaly-skills-verify-loop-20261017.md](./anomaly-skills-verify-loop-20261017.md) 记 **before→after**。禁止「只改文档/技能就收工」。

**Skills 到达层级（全文复用）**

| 层级 | 含义 |
|------|------|
| **L1 detect** | 已合入 detector 出 report（或明确 GAP） |
| **L2 class** | 现象类 / 根因 class 表命中（investigation） |
| **L3 module-bound** | verify PASS + ref-kv-dump 给出 token/层首分歧（仅 KV 可疑且有 dump） |
| **L4 root-cause** | **超出 skills** — 需人工白盒 / 上游 PR |

---

## 总表（检测 / 定位 / 帮助 / 定界）

列说明：**能否检测** = online detector 是否出 report；**能否定位** = 能否到算子/权重/commit（skills 几乎均为否）；**定界到哪** = skills 实际停点（L1 detect / L2 class-hint / L3 KV 首分歧）；**帮助程度** = 对排障是否有用。

| ID | class 短名 | 能否检测 | 能否定位 | 定界到哪 | 帮助 | repro vs 不复现（一句） |
|----|------------|----------|----------|----------|------|------------------------|
| S01 | KV skip-zero 有限垃圾 | **否** GAP | 否 | samples 类提示（弱 L2） | **中** | overlay 跳过 zero + 新 block；无 overlay / 少分配则无 |
| S02 | graph pad dirt | 未跑 | — | — | **低** | HARD-DEFER |
| S03 | CP slot mapping | 未跑 | — | — | **低** | HARD-DEFER / 需 CP |
| S04 | PD KV reformat | 未跑 | — | — | **低** | HCCN 阻塞 |
| S05 | spec rejection NaN | 未跑 | — | — | **低** | HARD-DEFER；≠S22 |
| S06 | MoE topk→0 | **是** `token_repeat` | 否 | **L2 class**（MoE 路由；KV finite≠根因） | **高** | MoE+overlay；dense/无 overlay 不复现 |
| S07 | W8A8 scale collapse | **否** GAP | 否 | samples identical+garbage（弱 L2） | **中** | W8A8+脏 scale；bf16 无 quant |
| S08 | slot→0 垃圾 | **是** `token_repeat` | 否 | L2（+可选 L3） | **高** | 错 slot overlay；冷 cache 可掩盖 |
| S09 | hybrid GDN pad | 未跑 | — | — | **低** | HARD-DEFER |
| S10′ | FullAttn recycle zero | **是** `token_repeat` | 否 | L2–**L3 潜力**（真 KV） | **高** | 关 zeroing+churn；APC 掩盖 |
| S11 | MLA RoPE pad | **是** `token_repeat` | 否 | **L2 class**（间接 KV） | **高** | MLA+pad-tail；无 pad 则弱 |
| S12 | packed KV stride | **是** `token_repeat` | 否 | L2–**L3 潜力** | **高** | page≠stride overlay；dense 且无 synth 弱 |
| S13 | hybrid Mamba recycle | 未跑 | — | — | **低** | FLA BLOCKED |
| S14 | MLA o_proj empty | **是** `token_repeat` | 否 | **L2 class** | **高** | graph+empty pad；eager 无 pad |
| S15 | MLA output pad stale | skip | — | — | **低** | 与 S14 重叠 |
| S16 | MoE router demote | **是** `token_repeat` | 否 | **L2 class** | **高** | MoE GateLinear demote；≠S06 |
| S17 | MoE routed_scale drop | **是** `token_repeat` | 否 | **L2 class** | **高** | Moonlight factor≠1；DSV2 factor=1 无效 |
| S18 | MoE shared combine skip | **是** `token_repeat` | 否 | **L2 class** | **高** | 需 shared experts |
| S19 | MoE topk renorm skip | **是** `token_repeat` | 否 | **L2 class** | **高** | `norm_topk_prob=True` |
| S20 | softcap/softmax 溢出 | **是** `token_repeat` | 否 | **L2 class-hint**（溢出塌缩类；非「仅 detect」） | **高** | 低 temp+unstable softmax；打错 V1 sampler 假阳 |
| S21 | dummy stale slot | 未跑 | — | — | **低** | SPEC / DP+spec |
| S22 | spec resample 无 SALT | **是** `spec_acceptance` | 否 | **L2 class**（RNG/SALT；分布性） | **高** | eagle3+temp>0；无 draft / 有 SALT 则否 |
| S23 | weight corrupt always-on | **是** `token_repeat` | 否 | **L1 only**（detect-only） | **中** | post-load 零一权重；干净 ckpt 对照 |
| S24 | quant scale always-on | **是** `token_repeat` | 否 | **L1 only**（≠ S07 GAP） | **中** | post-load 零一条 W8A8 scale；≠S07 路径触发 |
| S25 | RoPE 2nd-half drop | **是** `token_repeat` | 否 | **L2 class-hint**（RoPE half；≠S11） | **高** | soft-inv #7082；干净 rope 对照 |
| S26 | RMSNorm fp32-mul | **是** `token_repeat` | 否 | **L2 class-hint**（norm dtype） | **高** | soft-inv #42379；正确 dtype mul 对照 |
| S27 | MLA pe pre-sliced | — | — | — | **低** | **BLOCKED**（trig=0 + dirty clean） |
| S28 | RoPE neox→interleaved | **是** `token_repeat` | 否 | **L2 class-hint**（style flip） | **高** | soft-inv #7341/#7082；≠S25/S11 |
| S29 | logits fp16 demote | **是** `token_repeat` | 否 | **L2 class-hint**（cast；≠S20/S26） | **高** | V2 Sampler post-temp fp16 RT |
| S30 | null-block KV dirt | **是** `token_repeat` | 否 | **L2**（+可选 L3；≠S01/S10） | **高** | soft-inv #39444 block0 ones |
| S31 | residual stream drop | **是** `token_repeat` | 否 | **L2 class-hint**（≠S26） | **高** | add-rms 丢 residual accumulate |
| S32 | FIA FULL-graph pad | **是** `token_repeat` | 否 | **L2 class-hint**（≠S14） | **高** | soft-inv #7144 keep descriptor pad；unique `pad_echo` |
| S33 | incomplete softcap | **是** `token_repeat` | 否 | **L2 class-hint**（≠S20） | **高** | ÷cap+tanh skip *cap；≠ overflow/`!!!!` |
| S34 | attn scale drop | **是** `token_repeat` | 否 | **L2 class-hint**（≠S20/S32/S33） | **高** | 1/sqrt(d)→1.0 wrong attn temp；unique garbage |
| S35 | causal-off / future leak | **是** `token_repeat` | 否 | **L2 class-hint**（≠S34） | **高** | causal=False + mask=None |
| S36 | temp-scale blowup | **是** `token_repeat` | 否 | **L2 class-hint**（≠S29/S20） | **高** | post-temp ÷50；unique `id_echo`/`unique_garbage` |
| S37 | positions→0 before RoPE | **是** `token_repeat` | 否 | **L2 class-hint**（≠S25/S28/S11） | **高** | pos-collapse all tokens share pos-0 |
| S38 | RMSNorm identity skip | **是** `logits_finite` | 否 | **L2 class-hint**（≠S26/S31/S20） | **高** | skip npu_rms_norm → `!!!!` |
| S39 | SwiGLU skip-silu | **是** `logits_finite` | 否 | **L2 class-hint**（≠S26/S31/S38） | **高** | plain gate×up；skip npu_swiglu |
| S40 | RoPE skip | **是** `token_repeat` | 否 | **L2 class-hint**（≠S25/S28/S37） | **高** | unrotated Q/K；Nile phrase loop |
| S41 | post-FA attn ×1000 | **是** `logits_finite` | 否 | **L2 class-hint**（≠S34/S14/S35） | **高** | attn_out mul_(1000) after FA |
| S42 | RoPE phase negate | **是** `token_repeat` | 否 | **L2 class-hint**（≠S37/S40/S25/S28） | **高** | `-cos_sin` wrong phase |
| S43 | embed ×100 | **是** `token_repeat` | 否 | **L2 class-hint**（≠S23/S41） | **高** | vocab embed mul_(100)；`newline_collapse` |
| S44 | logits.zero_() | — | — | **BLOCKED** invalid-synthetic | **低** | PRINCIPLES §2 amplifier；非 PASS |
| S45 | top-k on `-logits` | **否** GAP | 否 | samples unique-garbage（弱 L2） | **中** | origin-faithful；detect=0；同 S01/S07 |
| S46 | penalty sign flip | **是** `token_repeat` | 否 | **L2 class-hint**（≠S45/S44） | **高** | 1/rep + neg freq/pres；digit collapse |
| S47 | K/V swap before FA | **是** `token_repeat` | 否 | **L2 class-hint**（≠S34/S35/S41） | **高** | swap K/V into attn；短语塌缩 |
| S48 | residual negate | **是** `logits_finite` | 否 | **L2 class-hint**（≠S31/S38） | **高** | `-residual` before add-RMSNorm；`!!!!` |
| S49 | attn scale ×50 | **是** `token_repeat` | 否 | **L2 class-hint**（≠S34/S41） | **高** | scale*50；unique/`1.1.1…` |
| S50 | SwiGLU half-swap | **是** `logits_finite` | 否 | **L2 class-hint**（≠S39） | **高** | `cat(up,gate)` then swiglu；`!!!!` |
| S51 | value ×50 before FA | **是** `token_repeat` | 否 | **L2 class-hint**（≠S41/S47/S49） | **高** | V magnitude blowup |
| S52 | query negate | **是** `token_repeat` | 否 | **L2 class-hint**（≠S47/S51/S42） | **高** | Q polarity flip before FA |
| S53 | logits ÷50 | **是** `token_repeat` | 否 | **L2 class-hint**（≠S36/S44） | **高** | lm-head scale-down |
| S54 | key negate | **是** `token_repeat` | 否 | **L2 class-hint**（≠S47/S51/S52） | **高** | K polarity flip before FA |
| S55 | residual ×50 | **是** `logits_finite` | 否 | **L2 class-hint**（≠S31/S38/S48） | **高** | residual magnitude blowup |
| S56 | SwiGLU input negate | **是** `logits_finite` | 否 | **L2 class-hint**（≠S39/S50） | **高** | `x=-x` before npu_swiglu |
| S57 | positions ×2 | **是** `token_repeat` | 否 | **L2 class-hint**（≠S37） | **高** | pos magnitude before RoPE |
| S58 | value negate | **是** `logits_finite` | 否 | **L2 class-hint**（≠S51/S47/S52/S54） | **高** | V polarity flip；`!!!!` |
| S59 | key ×50 | **是** `token_repeat` | 否 | **L2 class-hint**（≠S49/S51/S54） | **高** | K magnitude blowup |
| S60 | query ×50 | **是** `token_repeat` | 否 | **L2 class-hint**（≠S52/S49/S51/S59） | **高** | Q magnitude blowup |
| S61 | hidden ×50 | **是** `token_repeat` | 否 | **L2 class-hint**（≠S53/S43） | **高** | pre-lm-head hidden mag |
| S62 | pre-RMSNorm x×50 | **是** `logits_finite` | 否 | **L2 class-hint**（≠S26/S38/S48/S55） | **高** | pre-norm act mag；`!!!!` |
| S63 | attn-out negate | **是** `logits_finite` | 否 | **L2 class-hint**（≠S41） | **高** | post-FA polarity flip；`!!!!` |
| S64 | residual ÷50 | **是** `token_repeat` | 否 | **L2 class-hint**（≠S48/S55） | **高** | residual mag low |
| S65 | logits ×50 | **是** `token_repeat` | 否 | **L2 class-hint**（≠S53/S36） | **高** | lm-head mag high |
| S66 | RMSNorm weight negate | **是** `logits_finite` | 否 | **L2 class-hint**（≠S26/S38/S48/S55/S62） | **高** | `-weight` into add-RMSNorm；`!!!!` |
| S67 | SwiGLU out negate | **是** `logits_finite` | 否 | **L2 class-hint**（≠S39/S50/S56） | **高** | `-out` after npu_swiglu；`!!!!` |
| S68 | attn scale ÷50 | **是** `token_repeat` | 否 | **L2 class-hint**（≠S34/S49） | **高** | scale/50 wrong attn temp low |

> **S20 说明：** detector **能检出**（`token_repeat` 对 `!!!!`/token0）；skills 额外给出 **溢出/softcap class-hint（L2）**，不是「只能 detect、无类提示」。仍 **不能** 定位到具体 softcap 实现行或权重。

---

## 逐场景

### S01 — KV 新 block 未置零（有限垃圾）

| 项 | 内容 |
|----|------|
| **Class / PR** | `both` · vLLM#43990/#47574 · KV skip-zero |
| **现象** | mixed-script 有限垃圾 completion；无 NaN/Inf |
| **复现** | Qwen3-8B TP2；overlay 跳过 zero；冷启动突发新 block；`logits_finite` 武装 |
| **不复现** | 无 overlay；或新 block 很少 / APC 掩盖 |
| **Detector** | **GAP**（detect=0）；`logits_finite` miss |
| **Skills 最远** | L2 弱：`score_completion_samples` → garbage；**无 report** |
| **有用度** | **中** — 能归档 precision/GAP，无法 online 告警 |
| **待改进** | garbled-text detector；skills 与 DETECTOR_GAPS 联动清单 |

### S02 — Graph padding dirt

HARD-DEFER。skills 未应用。有用度 **低**（等 unpark）。待改进：与 S11/S14 切片关系写清。

### S03 — CP slot mapping

HARD-DEFER / 需 CP。有用度 **低**。

### S04 — PD KV reformat

SPEC+overlay 就绪；Ascend Mooncake 仍 **HCCN DOWN**。有用度 **低**（环境阻塞）。skills：有 dump 后可冲 L3。

### S05 — Spec rejection NaN

HARD-DEFER。≠ S22。有用度 **低**。

### S06 — MoE 路由偏置（topk→0）

| 项 | 内容 |
|----|------|
| **Class / PR** | `both` · 类比 vLLM#38989/#60946 · MoE 错专家 |
| **现象** | 复读 / 短乱码（如「惠惠感…」） |
| **复现** | DeepSeek-V2-Lite TP2 cards `0,1`（162）；overlay 强制错路由；`token_repeat` |
| **不复现** | 无 MoE / overlay 未 boot；dense-only |
| **Detector** | `token_repeat` |
| **Skills 最远** | L1–L2；verify 可得 PASS 但 **KV 全 finite** → L3 不定到 router |
| **有用度** | **高** — 典型「detect+分类」示范 |
| **待改进** | investigation 注明 MoE 类勿指望 KV 首分歧 |

### S07 — 量化 scale 崩溃（W8A8）

| 项 | 内容 |
|----|------|
| **Class / PR** | `both` · quant/scale 族 · W8A8 deq collapse |
| **现象** | **48/48 identical** mixed-script 垃圾 |
| **复现** | Qwen3-8B-W8A8 TP2 cards `0,1`（162）；overlay 脏 deq_scale；高 trigger |
| **不复现** | bf16 无 quant；FP8 lab 不能跑 |
| **Detector** | **GAP** |
| **Skills 最远** | L2 弱：identical+garbage 评分；**不能**指出哪条 scale |
| **有用度** | **中** — GAP 证据完整；无定位 |
| **待改进** | 与下方 **Q-stub** 区分（S07=路径触发；Q-stub=always-on） |

### S08 — slot/index→0 垃圾复读

| 项 | 内容 |
|----|------|
| **Class / PR** | `both` · 模式类比 vLLM#45324 · decode index 错 |
| **现象** | 重复垃圾 token |
| **复现** | Qwen3-8B TP2；overlay 强制 slot0；预热后再开 overlay；`token_repeat` |
| **不复现** | 冷 cache 且无触发 predicate；禁 overlay |
| **Detector** | `token_repeat`（status PASS） |
| **Skills 最远** | L1–L2；有 dump 可试 L3 |
| **有用度** | **高** |
| **待改进** | fail-evidence 与 status PASS 对齐归档 |

### S09 — Hybrid GDN pad write

HARD-DEFER。有用度 **低**。

### S10′ — FullAttention 回收 block 未置零

| 项 | 内容 |
|----|------|
| **Class / PR** | `both` · vLLM#39283/#43741 |
| **现象** | xxxx/复读塌缩；temp=0 发散 |
| **复现** | Qwen3-8B TP2 `4,5`；`needs_kv_cache_zeroing=False`；util≈0.35；无 APC；并发 churn；`token_repeat` |
| **不复现** | 开 APC；无 recycle；CJK 误判 precision（勿用） |
| **Detector** | `token_repeat`（65/20/79） |
| **Skills 最远** | L1–**L3 潜力**（真 KV 污染） |
| **有用度** | **高** |
| **待改进** | 标准 ref-kv 跑通 checklist |

### S11 — MLA RoPE pad 错位

| 项 | 内容 |
|----|------|
| **Class / PR** | `ascend-only` · ascend#18798 |
| **现象** | digit/junk；temp=0 发散 |
| **复现** | DeepSeek-V2-Lite MLA bf16 TP2；pad-tail overlay；util≈0.40；无 APC |
| **不复现** | 无 pad（eager 且无 graph pad）；fp16 gather 崩（环境，非 FAIL） |
| **Detector** | `token_repeat`（138/39/60） |
| **Skills 最远** | L1–L2（间接 KV；dump 未必指向 RoPE） |
| **有用度** | **高** |
| **待改进** | class 表标明「间接 KV → L3 弱」 |

### S12 — Packed KV zero stride 错

| 项 | 内容 |
|----|------|
| **Class / PR** | `both` · vLLM#50276 |
| **现象** | `000…` / echo / collapse |
| **复现** | Qwen3-8B TP2；page-as-stride overlay；并发 churn；`token_repeat` |
| **不复现** | dense page==stride 且无 synth；无 zeroer |
| **Detector** | `token_repeat`（132/1/79） |
| **Skills 最远** | L1–**L3 潜力** |
| **有用度** | **高** |

### S13 — Hybrid Mamba recycle

BLOCKED（FLA CausalConv1d）。有用度 **低**。

### S14 — MLA o_proj pad 未初始化

| 项 | 内容 |
|----|------|
| **Class / PR** | `ascend-only` · ascend#9687 |
| **现象** | digit/echo/junk |
| **复现** | DeepSeek-V2-Lite-W8A8 **graph** TP2；zeros→empty；util≈0.35 |
| **不复现** | `--enforce-eager`（无 pad）；bf16 路径弱 |
| **Detector** | `token_repeat`（128/5/60） |
| **Skills 最远** | L1–L2 |
| **有用度** | **高** |

### S15 — MLA output pad stale

skip（与 S14 重叠）。有用度 **低**。

### S16 — MoE router logits demote

| 项 | 内容 |
|----|------|
| **Class / PR** | `both` · ascend#16189 / vLLM#38989 |
| **现象** | 复读/塌缩 |
| **复现** | DeepSeek-V2-Lite bf16；GateLinear fp32→bf16 demote；≠ S06 force-expert0 |
| **不复现** | dense；overlay 未打到 GateLinear |
| **Detector** | `token_repeat`（372/5/60） |
| **Skills 最远** | L1–L2 |
| **有用度** | **高** |

### S17 — MoE routed_scaling_factor drop

| 项 | 内容 |
|----|------|
| **Class / PR** | `both` · ascend#9036 / vLLM#43769 |
| **现象** | `. 0. 0.` / ctx_echo |
| **复现** | Moonlight-16B-A3B（factor≠1）；skip output scale |
| **不复现** | DeepSeek-V2-Lite（factor=1 → 软逆无效） |
| **Detector** | `token_repeat`（448/43/60） |
| **Skills 最远** | L1–L2 |
| **有用度** | **高** |

### S18 — MoE shared+routed combine skip

| 项 | 内容 |
|----|------|
| **Class / PR** | `ascend-only` · ascend#16245/#16550 |
| **现象** | digit/`***`/ZWSP |
| **复现** | DeepSeek-V2-Lite（n_shared_experts=2）；skip foreach_add |
| **不复现** | 无 shared experts |
| **Detector** | `token_repeat`（370/15/58） |
| **Skills 最远** | L1–L2 |
| **有用度** | **高** |

### S19 — MoE topk renorm skip

| 项 | 内容 |
|----|------|
| **Class / PR** | `both` · ascend#9692 / norm_topk_prob |
| **现象** | prompt/ctx echo |
| **复现** | Moonlight（norm_topk_prob=True）；renorm=0 |
| **不复现** | DeepSeek-V2-Lite（norm_topk_prob=False） |
| **Detector** | `token_repeat`（448/42/60） |
| **Skills 最远** | L1–L2 |
| **有用度** | **高** |

### S20 — Softcap / 不稳定 softmax 数值溢出（constructed）

| 项 | 内容 |
|----|------|
| **Class / PR** | constructed · 类比 vLLM#56579 |
| **现象** | 全请求 `!!!!…`（token0） |
| **复现** | Qwen3-8B；V2 Sampler unstable softmax；**temp=0.05**；`token_repeat` |
| **不复现** | temp≈1 且无溢出；只打 V1 AscendTopKTopPSampler（假 detect） |
| **能否检测** | **是** — `token_repeat`（130/48/48）；`logits_finite` 可能 miss |
| **能否定位** | **否** — 不到 softcap 源码行 / 权重 |
| **定界到哪** | **L2 class-hint**：溢出→token0 塌缩类（skills 表已收录）；**不是** detect-only |
| **有用度** | **高** |
| **待改进** | 已有 v1.3；可选记录 absmax 触发阈值 |

### S21 — Dummy 陪跑 stale slot

SPEC/in progress（DP+spec）。有用度 **低**（未 PASS）。

### S22 — Spec residual resample 无 SALT

| 项 | 内容 |
|----|------|
| **Class / PR** | `ascend-only` · ascend#18657（G2 本就无 SALT） |
| **现象** | 接受率 0–0.27；文本可看似正常 |
| **复现** | Qwen3-8B+eagle3；temp=0.8；num_spec=3；`spec_acceptance` |
| **不复现** | 无 draft；temp=0；已合入 SALT 的树 |
| **Detector** | `spec_acceptance` 主 + 少量 `token_repeat`（130/45/48） |
| **Skills 最远** | L1–L2（分布性；samples 评分弱） |
| **有用度** | **高** |
| **待改进** | analysis 摘要 acceptance_rate 字段（已部分在 v1.4） |

---

### S23 — 权重层腐蚀 always-on（constructed）

| 项 | 内容 |
|----|------|
| **意图 / 现象** | post-`load_model` 零掉一层 `o_proj.weight`；启动后恒定复读/塌缩 |
| **三层率** | **2 / 17 / 48**；detect = `token_repeat`×48（evidence @ `1f6fc18`） |
| **能否检测** | **是** |
| **能否定位** | **否** — 禁止从 dump/ref 推断「哪条 weight」 |
| **Skills 最远** | **L1 detect-only** |
| **有用度** | **中** — 验证 always-on 可捕；负对照=干净 ckpt |
| **待改进** | 无（本 class 故意停在 L1） |

### S24 — W8A8 weight_scale 置零 always-on（constructed；≠ S07）

| 项 | 内容 |
|----|------|
| **意图 / 现象** | post-load 零一条 `weight_scale`；每请求 `token_repeat`；samples 可混 digits/repeat + 偶发 garbage 标签 |
| **三层率** | **2 / 48 / 48**；detect = `token_repeat`×48 |
| **能否检测** | **是**（≠ S07 FAIL+GAP） |
| **能否定位** | **否** — 不能指出哪条 scale |
| **Skills 最远** | **L1 detect-only** |
| **有用度** | **中** — 与 S07「路径触发+GAP」对照 |
| **待改进** | score 已修：混有 `garbage_mixed_script` 时勿批发 GAP（v1.5） |

---

### S25 — RoPE 第二半写丢（soft-inv #7082）

| 项 | 内容 |
|----|------|
| **三层率** | **462 / 15 / 48**；`token_repeat`×48 |
| **能否检测** | **是** |
| **Skills 最远** | **L2 class-hint**（RoPE half-drop）；≠ S11 pad |
| **有用度** | **高** |
| **待改进** | 无（不定位 Triton store 行） |

### S26 — RMSNorm fp32 weight-mul（soft-inv #42379）

| 项 | 内容 |
|----|------|
| **三层率** | **470 / 14 / 48**；`token_repeat`×48 |
| **能否检测** | **是** |
| **Skills 最远** | **L2 class-hint**（norm dtype/cast） |
| **有用度** | **高** |
| **待改进** | 症状可与 S25 重叠 → 靠场景/overlay 区分 |

### S28 — RoPE neox→interleaved（#7341/#7082 class）

| 项 | 内容 |
|----|------|
| **三层率** | **462 / 16 / 48**；`token_repeat`×48 |
| **能否检测** | **是** |
| **Skills 最远** | **L2 class-hint**（style flip）；≠ S25/S11 |
| **有用度** | **高** |
| **待改进** | score **v1.6** 补 `phrase_repeat`（句级复读） |

### S29 — Logits fp16 demote（sampling/cast）

| 项 | 内容 |
|----|------|
| **三层率** | **132 / 14 / 48**；`token_repeat`×48 |
| **能否检测** | **是** |
| **Skills 最远** | **L2 class-hint**（cast）；≠ S20 softcap ≠ S26 |
| **有用度** | **高** |
| **待改进** | 无（不定位 Sampler 行） |

### S30 — Null-block KV dirt（soft-inv #39444）

| 项 | 内容 |
|----|------|
| **三层率** | **2 / 14 / 48**；`token_repeat`×48 |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（+可选 L3）；≠ S01/S10/S23/S24 |
| **有用度** | **高** |
| **待改进** | 可选标准 ref-kv 流水线 |

### S31 — Residual stream drop（≠ S26）

| 项 | 内容 |
|----|------|
| **三层率** | **470 / 48 / 48**；`token_repeat`×48；identical `FieldType` 复读 |
| **能否检测** | **是** |
| **Skills 最远** | **L2 class-hint**（丢 residual accumulate）；≠ S26 fp32-mul |
| **有用度** | **高** |
| **待改进** | 无 |

### S32 — FIA FULL-graph pad（soft-inv #7144；≠ S14）

| 项 | 内容 |
|----|------|
| **三层率** | **132 / 47 / 48**；`token_repeat`×48；precision=unique garbage（identical-mode 低估） |
| **能否检测** | **是** |
| **Skills 最远** | **L2 class-hint**（FULL keep descriptor pad）；score **`pad_echo`**；≠ S14 o_proj empty |
| **有用度** | **高** |
| **待改进** | 无 |

### S33 — Incomplete softcap（≠ S20）

| 项 | 内容 |
|----|------|
| **三层率** | **132 / 15 / 48**；`token_repeat`×48；mode `1.1.1…` |
| **能否检测** | **是** |
| **Skills 最远** | **L2 class-hint**（÷cap+tanh skip *cap）；≠ S20 overflow/`!!!!` |
| **有用度** | **高** |
| **待改进** | 无 |

### S34 — Attn scale drop（1/sqrt(d)→1.0；≠ S20/S32/S33）

| 项 | 内容 |
|----|------|
| **三层率** | **18 / 26 / 48**；`token_repeat`×48；precision=unique digit/junk |
| **能否检测** | **是** |
| **Skills 最远** | **L2 class-hint**（wrong attn temperature）；≠ S20/S32/S33 |
| **有用度** | **高** |
| **待改进** | 无 |

### S35 — Causal-off / future leak（≠ S34）

| 项 | 内容 |
|----|------|
| **三层率** | **136 / 46 / 48**；`token_repeat`×48；强 `phrase_repeat` |
| **能否检测** | **是** |
| **Skills 最远** | **L2 class-hint**（non-causal / mask=None）；≠ S34 scale |
| **有用度** | **高** |
| **待改进** | 无 |

### S36 — Temp-scale blowup（÷50；≠ S29/S20）

| 项 | 内容 |
|----|------|
| **三层率** | **132 / 10 / 19**；`token_repeat`×19；unique garbled / id-echo |
| **能否检测** | **是** |
| **Skills 最远** | **L2**；score **`id_echo`/`unique_garbage`**（hits 4→33）；≠ S29/S20 |
| **有用度** | **高** |
| **待改进** | 无 |

### S37 — Positions→0 before RoPE（≠ S25/S28/S11）

| 项 | 内容 |
|----|------|
| **三层率** | **132 / 35 / 48**；`token_repeat`×48 |
| **能否检测** | **是** |
| **Skills 最远** | **L2 class-hint**（pos-collapse）；≠ S25/S28/S11 |
| **有用度** | **高** |
| **待改进** | 无 |

### S38 — RMSNorm identity skip（≠ S26/S31/S20）

| 项 | 内容 |
|----|------|
| **三层率** | **188 / 48 / 48**；**`logits_finite`×48**；identical `!!!!` |
| **能否检测** | **是**（主 detector=`logits_finite`） |
| **Skills 最远** | **L2**；≠ S26 fp32-mul ≠ S31 residual ≠ S20 softcap path |
| **有用度** | **高** |
| **待改进** | 无 |

### S39 — SwiGLU skip-silu（≠ S26/S31/S38）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 48 / 48**；**`logits_finite`×48**；identical `!!!!` |
| **能否检测** | **是**（主=`logits_finite`） |
| **Skills 最远** | **L2**（activation skip）；≠ S26/S31/S38 |
| **有用度** | **高** |
| **待改进** | 无 |

### S40 — RoPE skip（unrotated Q/K；≠ S25/S28/S37）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 45 / 48**；`token_repeat`×48；强 Nile `phrase_repeat` |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（no rotary）；≠ S25 half ≠ S28 style ≠ S37 pos-zero |
| **有用度** | **高** |
| **待改进** | 无 |

### S41 — Post-FA attn out ×1000（≠ S34/S14/S35）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 48 / 48**；**`logits_finite`×48**；identical `!!!!` |
| **能否检测** | **是**（主=`logits_finite`） |
| **Skills 最远** | **L2**（wrong attn-out scale）；≠ S34 softmax-scale ≠ S14/S35 |
| **有用度** | **高** |
| **待改进** | 无 |

### S42 — RoPE phase negate（`-cos_sin`；≠ S37/S40/S25/S28）

| 项 | 内容 |
|----|------|
| **三层率** | **16 / 16 / 48**；`token_repeat`×48 |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong RoPE phase）；≠ S37/S40/S25/S28 |
| **有用度** | **高** |
| **待改进** | 无 |

### S43 — Embed scale ×100（≠ S23/S41）

| 项 | 内容 |
|----|------|
| **三层率** | **16 / 40 / 48**；`token_repeat`×48；newline collapse |
| **能否检测** | **是** |
| **Skills 最远** | **L2**；score **`newline_collapse`**（hits 0→40）；≠ S23/S41 |
| **有用度** | **高** |
| **待改进** | 无 |

### S44 — Logits `zero_()` — **BLOCKED / invalid-synthetic**

| 项 | 内容 |
|----|------|
| **三层率** | 16/48/48 `token_repeat`（`!!!!`）— **不计入 PASS** |
| **能否检测** | 可亮灯，但是 **amplifier** |
| **Skills 最远** | **拒收**：`processed_logits.zero_()` 发明症状（PRINCIPLES §2）；negate 失败后改写为零 ≠ origin-faithful |
| **有用度** | **低** |
| **待改进** | 若有真实「logits 丢弃/未写」bug 路径再 origin 重做；否则保持 BLOCKED |

### S45 — Top-k on `-logits`（unique garbage）— **FAIL+GAP**

| 项 | 内容 |
|----|------|
| **三层率** | **16 / unique / 0**；score `precision_hits=47`（`garbage_mixed_script`×44）；identical-mode 低估 |
| **能否检测** | **否** GAP（`token_repeat`/`logits_finite` miss） |
| **Skills 最远** | 弱 L2：归档 samples + `WHY_UNDETECTED`；**无 online report** |
| **有用度** | **中** — 诚实 FAIL+GAP（同 S01/S07）；勿放大器硬凑 |
| **待改进** | garbled / unique-garbage detector；对比 S46 已 detect 的 sampling soft-inv |

### S46 — Penalty sign flip（≠ S45/S44）

| 项 | 内容 |
|----|------|
| **三层率** | **16 / 48 / 48**；`token_repeat`×48 |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（penalty polarity invert → digit/`1.1.1…`）；≠ S45 GAP ≠ S44 amplifier |
| **有用度** | **高** |
| **待改进** | 无 |

### S47 — K/V swap before FA（≠ S34/S35/S41）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 37 / 48**；`token_repeat`×48 |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（K/V swapped into attn）；短语/单字塌缩；≠ S34 scale ≠ S35 causal ≠ S41 attn-out |
| **有用度** | **高** |
| **待改进** | 有 dump 时可冲 L3；本轮 offline 停在 L2 |

### S48 — Residual negate（≠ S31/S38）

| 项 | 内容 |
|----|------|
| **三层率** | **100 / 48 / 48**；**`logits_finite`×48**；identical `!!!!` |
| **能否检测** | **是**（主=`logits_finite`） |
| **Skills 最远** | **L2**（wrong residual polarity）；≠ S31 drop ≠ S38 skip |
| **有用度** | **高** |
| **待改进** | 无 |

### S49 — Attn scale ×50（≠ S34/S41）

| 项 | 内容 |
|----|------|
| **三层率** | **18 / 22 / 48**；`token_repeat`×48 |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（attn temp too hot）；unique/`1.1.1…`；≠ S34 scale→1.0 ≠ S41 post-FA |
| **有用度** | **高** |
| **待改进** | 无 |

### S50 — SwiGLU gate/up half-swap（≠ S39）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 48 / 48**；**`logits_finite`×48**；identical `!!!!` |
| **能否检测** | **是**（主=`logits_finite`） |
| **Skills 最远** | **L2**（halves swapped）；≠ S39 skip-silu |
| **有用度** | **高** |
| **待改进** | 无 |


### S51 — Value ×50 before FA（≠ S41/S47/S49）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 48 / 48**；`token_repeat`×48（layers；reports/samples not mirrored） |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong V magnitude）；≠ S41 attn-out ≠ S47 K/V ≠ S49 attn-scale |
| **有用度** | **高** |
| **待改进** | builder 可回填 reports/samples |

### S52 — Query negate（≠ S47/S51/S42）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 26 / 48**；`token_repeat`×48（layers） |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong Q polarity）；≠ S47/S51/S42 |
| **有用度** | **高** |
| **待改进** | builder 可回填 reports/samples |

### S53 — LM-head logits ÷50（≠ S36/S44）

| 项 | 内容 |
|----|------|
| **三层率** | **16 / 16 / 48**；`token_repeat`×48（layers） |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong lm-head scale）；≠ S36 post-temp ÷50 ≠ S44 zero_ |
| **有用度** | **高** |
| **待改进** | builder 可回填 reports/samples |


### S54 — Key negate（≠ S47/S51/S52）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 26 / 48**；`token_repeat`×48（slim layers） |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong K polarity）；≠ S47/S51/S52 |
| **有用度** | **高** |
| **待改进** | builder 可回填 reports/samples |

### S55 — Residual ×50（≠ S31/S38/S48）

| 项 | 内容 |
|----|------|
| **三层率** | **100 / 48 / 48**；**`logits_finite`×48**；identical `!!!!` |
| **能否检测** | **是**（主=`logits_finite`） |
| **Skills 最远** | **L2**（wrong residual magnitude）；≠ S31 drop ≠ S38 skip ≠ S48 sign-flip |
| **有用度** | **高** |
| **待改进** | 无（slim pack OK for L2） |

### S56 — SwiGLU input negate（≠ S39/S50）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 48 / 48**；**`logits_finite`×48**；identical `!!!!` |
| **能否检测** | **是**（主=`logits_finite`） |
| **Skills 最远** | **L2**（wrong SwiGLU input sign）；≠ S39 skip ≠ S50 half-swap |
| **有用度** | **高** |
| **待改进** | 无 |


### S57 — Positions ×2 before RoPE（≠ S37）

| 项 | 内容 |
|----|------|
| **三层率** | **132 / 48 / 48**；`token_repeat`×48（slim） |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong pos magnitude）；≠ S37 pos-zero |
| **有用度** | **高** |
| **待改进** | 无 |

### S58 — Value negate（≠ S51/S47/S52/S54）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 48 / 48**；**`logits_finite`×48**；identical `!!!!` |
| **能否检测** | **是**（主=`logits_finite`） |
| **Skills 最远** | **L2**（wrong V polarity）；≠ S51 V×50 ≠ S47/S52/S54 |
| **有用度** | **高** |
| **待改进** | 无 |

### S59 — Key ×50（≠ S49/S51/S54）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 15 / 48**；`token_repeat`×48（slim） |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong K magnitude）；≠ S49 attn-scale ≠ S51 V×50 ≠ S54 K-negate |
| **有用度** | **高** |
| **待改进** | 无 |


### S60 — Query ×50（≠ S52/S49/S51/S59）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 23 / 48**；`token_repeat`×48（slim） |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong Q magnitude）；≠ S52 negate ≠ S49/S51/S59 |
| **有用度** | **高** |
| **待改进** | 无 |

### S61 — Hidden ×50 before lm-head（≠ S53/S43）

| 项 | 内容 |
|----|------|
| **三层率** | **16 / 16 / 48**；`token_repeat`×48（slim） |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong pre-head hidden mag）；≠ S53 logits÷50 ≠ S43 embed |
| **有用度** | **高** |
| **待改进** | 无 |

### S62 — Pre-RMSNorm x×50（≠ S26/S38/S48/S55）

| 项 | 内容 |
|----|------|
| **三层率** | **100 / 48 / 48**；**`logits_finite`×48**；identical `!!!!` |
| **能否检测** | **是**（主=`logits_finite`） |
| **Skills 最远** | **L2**（wrong pre-norm act mag）；≠ S26/S38/S48/S55 |
| **有用度** | **高** |
| **待改进** | 无 |


### S63 — Attn-out negate（≠ S41）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 48 / 48**；**`logits_finite`×48**；identical `!!!!` |
| **能否检测** | **是**（主=`logits_finite`） |
| **Skills 最远** | **L2**（wrong attn-out polarity）；≠ S41 ×1000 |
| **有用度** | **高** |
| **待改进** | 无 |

### S64 — Residual ÷50（≠ S48/S55）

| 项 | 内容 |
|----|------|
| **三层率** | **100 / 48 / 48**；`token_repeat`×48（slim） |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong residual mag low）；≠ S48 sign ≠ S55 ×50 |
| **有用度** | **高** |
| **待改进** | 无 |

### S65 — Logits ×50（≠ S53/S36）

| 项 | 内容 |
|----|------|
| **三层率** | **16 / 16 / 48**；`token_repeat`×48（slim） |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong logit mag high）；≠ S53 ÷50 ≠ S36 temp |
| **有用度** | **高** |
| **待改进** | 无 |

### S66 — RMSNorm weight negate（≠ S26/S38/S48/S55/S62）

| 项 | 内容 |
|----|------|
| **三层率** | **100 / 48 / 48**；**`logits_finite`×48**；identical `!!!!` |
| **能否检测** | **是**（主=`logits_finite`） |
| **Skills 最远** | **L2**（wrong norm-weight sign）；≠ S26/S38/S48/S55/S62 |
| **有用度** | **高** |
| **待改进** | 无 |

### S67 — SwiGLU out negate（≠ S39/S50/S56）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 48 / 48**；**`logits_finite`×48**；identical `!!!!` |
| **能否检测** | **是**（主=`logits_finite`） |
| **Skills 最远** | **L2**（wrong SwiGLU out polarity）；≠ S39/S50/S56 |
| **有用度** | **高** |
| **待改进** | 无 |

### S68 — Attn scale ÷50（≠ S34/S49）

| 项 | 内容 |
|----|------|
| **三层率** | **18 / 33 / 48**；`token_repeat`×48（slim） |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（attn temp too cold）；≠ S34→1.0 ≠ S49×50 |
| **有用度** | **高** |
| **待改进** | 无 |

---

## Verify-loop deltas（2026-10-17）

| ID | Before → After | 是否达到预期 |
|----|----------------|--------------|
| **S20** | score 误标 GAP → **无 GAP** + `token0_collapse`；叙事升为 **L2 class-hint** | **是** |
| **S22** | 无 RNG/SALT class → **L2** via `spec_acceptance` | **是** |
| **S23** | stub → **PASS L1 detect-only** | **是** |
| **S24** | score **假 GAP** → **无 GAP**；≠ S07 | **是** |
| **S06/S08/S10′/S11/S12/S14/S16–S19** | 补跑 verify：skills 表已够 → **无改 skill**；S06 补 PASS 归档 | **是**（no-edit） |
| **S01/S07** | 复验仍 **FAIL+GAP**（score 正确给 gap hint / status detect=0） | **是**（GAP 诚实） |
| **S25** | 无 RoPE half class → **L2** + `token_repeat`；score 已有 `repeat` | **是** |
| **S26** | 无 RMSNorm dtype class → **L2** + `token_repeat` | **是** |
| **S28** | score **precision_hits=0**（句级复读漏标）→ **`phrase_repeat`×8**；skills **L2** style flip | **是** |
| **S29** | 无 cast class → **L2** logits fp16 demote；≠ S20/S26 | **是** |
| **S30** | 无 null-block class → **L2** KV dirt；≠ S01/S10 | **是** |
| **S31** | 无 residual-drop class → **L2**；≠ S26；score identical phrase OK | **是** |
| **S32** | score precision_hits=4（漏 unique pad）→ **`pad_echo`×45 / hits=48**；skills **L2** ≠ S14 | **是** |
| **S33** | 无 incomplete-softcap class（易混 S20）→ **L2**；score 已有 repeat | **是** |
| **S34** | 无 attn-scale class → **L2** wrong attn temp；≠ S20/S32/S33 | **是** |
| **S35** | 无 causal-off class → **L2** future leak；≠ S34 | **是** |
| **S36** | score hits=4（漏 unique id-echo）→ **`unique_garbage`/`id_echo` hits=33**；**L2** ≠ S29/S20 | **是** |
| **S37** | 无 pos-collapse class → **L2**；≠ S25/S28/S11 | **是** |
| **S38** | 无 RMSNorm-skip class；易混 S20 → **L2** via **`logits_finite`** | **是** |
| **S39** | 无 SwiGLU-skip class → **L2** via **`logits_finite`**；≠ S26/S31/S38 | **是** |
| **S40** | 无 RoPE-skip class → **L2**；≠ S25/S28/S37 | **是** |
| **S41** | 无 attn-out-scale class → **L2** via **`logits_finite`**；≠ S34/S14/S35 | **是** |
| **S42** | 无 RoPE-phase class → **L2**；≠ S37/S40/S25/S28 | **是** |
| **S43** | score hits=0（纯换行漏标）→ **`newline_collapse`×40**；**L2** ≠ S23/S41 | **是** |
| **S44** | amplifier `zero_()` → **BLOCKED**（非 skills win） | **是**（诚实拒收） |
| **S45** | unique garbage detect=0 → **FAIL+GAP**（同 S01/S07）；≥3 samples + `WHY_UNDETECTED` | **是**（诚实 GAP） |
| **S46** | 无 penalty-polarity class → **L2**；≠ S45/S44 | **是** |
| **S47** | 无 K/V-swap class → **L2**；≠ S34/S35/S41 | **是** |
| **S48** | 无 residual-negate class → **L2** via **`logits_finite`**；≠ S31/S38 | **是** |
| **S49** | 无 attn×50 class → **L2**；≠ S34/S41 | **是** |
| **S50** | 无 SwiGLU-swap class → **L2** via **`logits_finite`**；≠ S39 | **是** |
| **S51** | 无 V-scale class → **L2**；≠ S41/S47/S49 | **是** |
| **S52** | 无 Q-negate class → **L2**；≠ S47/S51/S42 | **是** |
| **S53** | 无 logits÷50 class → **L2**；≠ S36/S44 | **是** |
| **S54** | 无 K-negate class → **L2**；≠ S47/S51/S52 | **是** |
| **S55** | 无 residual×50 class → **L2** via **`logits_finite`**；≠ S31/S38/S48 | **是** |
| **S56** | 无 SwiGLU-input-negate class → **L2** via **`logits_finite`**；≠ S39/S50 | **是** |
| **S57** | 无 positions×2 class → **L2**；≠ S37 | **是** |
| **S58** | 无 V-negate class → **L2** via **`logits_finite`**；≠ S51/S47/S52/S54 | **是** |
| **S59** | 无 K×50 class → **L2**；≠ S49/S51/S54 | **是** |
| **S60** | 无 Q×50 class → **L2**；≠ S52/S49/S51/S59 | **是** |
| **S61** | 无 hidden×50 class → **L2**；≠ S53/S43 | **是** |
| **S62** | 无 pre-norm x×50 class → **L2** via **`logits_finite`**；≠ S26/S38/S48/S55 | **是** |
| **S63** | 无 attn-out-negate class → **L2** via **`logits_finite`**；≠ S41 | **是** |
| **S64** | 无 residual÷50 class → **L2**；≠ S48/S55 | **是** |
| **S65** | 无 logits×50 class → **L2**；≠ S53/S36 | **是** |
| **S66** | 无 RMSNorm-weight-negate class → **L2** via **`logits_finite`**；≠ S26/S38/S48/S55/S62 | **是** |
| **S67** | 无 SwiGLU-out-negate class → **L2** via **`logits_finite`**；≠ S39/S50/S56 | **是** |
| **S68** | 无 attn-scale÷50 class → **L2**；≠ S34/S49 | **是** |

详见 [anomaly-skills-verify-loop-20261017.md](./anomaly-skills-verify-loop-20261017.md)。

## Skills 全局缺口（优先序）

1. **Garbled / identical-across / unique-garbage detector**（解锁 S01/S07/**S45** → 可升「高」有用度的 online 段）  
2. MoE/溢出类：**明确 L3 不可达**（避免空跑 ref）  
3. Spec 分布性：summarize 突出 `acceptance_rate`  
4. ~~Weight/Quant always-on 场景落地~~ → **S23/S24 PASS L1**（仍不可定位张量）  
5. KV PASS（S10′/S12/S30/S47）：标准 ref-kv 流水线模板 + 容器 dump_dir 重映射  
6. Soft-inv / cast / residual / graph-pad / softcap / attn / temp / pos / norm / act / rope / embed / penalty / kv-swap / **residual-negate / attn×50 / swiglu-swap / norm-weight-negate / swiglu-out-negate / attn÷50**：**S25–S68 L2**（除 S44 INVALID / S45 FAIL+GAP）

---

## 如何续写本文

1. 160 在 handoff Inbox 追加一行 → skills 方拉 fail-evidence。  
2. 跑 `summarize_reports` / `score_completion_samples` /（可选）`verify_request_kv`。  
3. 在本文件「逐场景」追加一节 + 更新总表有用度。  
4. 新 class → 改 `analysis/skill/` 并 bump `SKILLS_METADATA` → `git push main`。  
5. 同步 AgentStore：`docs/anomaly-skills-capability-20261017.md` 与 `docs/anomaly-skills-runs/`。

**证据索引：** `tests/build-anomaly-env/fail-evidence/Sxx/` · 店内 `docs/anomaly-skills-runs/` · `docs/anomaly-skills-analysis-20261017.md`
