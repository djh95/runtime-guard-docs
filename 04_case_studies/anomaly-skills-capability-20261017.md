# Anomaly × Skills 能力边界（活文档）— 2026-10-17

> **用途：** 对每一个已落地 / 在册异常场景，如实记录现象、复现与对照配置、skills 能分析到哪一步、有用度，以及还缺什么。  
> **Skills：** `runtime-guard-test` `analysis/skill/` **v5.7**（investigation / detector-sweep / config-recommender / analysis / ref-kv-dump）。  
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
| S69 | embed negate | **是** `logits_finite` | 否 | **L2 class-hint**（≠S43） | **高** | embed polarity flip；`!!!!` |
| S70 | variance eps ×1000 | **是** `token_repeat` | 否 | **L2 class-hint**（≠S26/S38/S66） | **高** | wrong norm eps；`1.1.1…` |
| S71 | RMSNorm weight ×50 | **是** `logits_finite` | 否 | **L2 class-hint**（≠S66） | **高** | weight mag blowup；`!!!!` |
| S72 | SwiGLU out ×50 | **是** `logits_finite` | 否 | **L2 class-hint**（≠S39/S50/S56/S67） | **高** | out mag blowup；`!!!!` |
| S73 | RMSNorm x negate | **是** `logits_finite` | 否 | **L2 class-hint**（≠S48/S62） | **高** | pre-norm act polarity；`!!!!` |
| S74 | RMSNorm weight ÷50 | **是** `token_repeat` | 否 | **L2 class-hint**（≠S66/S71） | **高** | weight mag low；phrase repeat |
| S75 | hidden ÷50 | **是** `token_repeat` | 否 | **L2 class-hint**（≠S61/S53/S65） | **高** | pre-head hidden mag low |
| S76 | SwiGLU input ×50 | **是** `logits_finite` | 否 | **L2 class-hint**（≠S39/S50/S56/S67/S72） | **高** | input mag blowup；`!!!!` |
| S77 | variance eps ÷1000 | **是** `token_repeat` | 否 | **L2 class-hint**（≠S70） | **高** | norm eps low |
| S78 | RMSNorm x ÷50 | **是** `token_repeat` | 否 | **L2 class-hint**（≠S62/S73） | **高** | pre-norm act mag low |
| S79 | cos_sin ×50 | **是** `token_repeat` | 否 | **L2 class-hint**（≠S37/S40/S42/S25/S28） | **高** | rope phase mag blowup |
| S80 | embed ÷50 | **是** `token_repeat` | 否 | **L2 class-hint**（≠S43/S69） | **高** | embed mag low；detect 可 <n_req |
| S81 | SwiGLU input ÷50 | **是** `token_repeat` | 否 | **L2 class-hint**（≠S39/S50/S56/S76） | **高** | input mag low；phrase repeat |
| S82 | cos_sin ÷50 | **是** `token_repeat` | 否 | **L2 class-hint**（≠S37/S40/S42/S79） | **高** | rope phase mag low |
| S83 | attn-out ×50 | **是** `token_repeat` | 否 | **L2 class-hint**（≠S41/S63） | **高** | milder than S41×1000；`token_repeat` |
| S84 | positions ÷2 | **是** `token_repeat` | 否 | **L2 class-hint**（≠S37/S57） | **高** | floor-div before rope |
| S85 | temp ÷50 | **是** `token_repeat` | 否 | **L2 class-hint**（≠S36） | **高** | post-temp×50；需 T>0 |
| S86 | RMSNorm-out negate | **是** `logits_finite` | 否 | **L2 class-hint**（≠S73/S66） | **高** | post-norm polarity；`!!!!` |
| S87 | RMSNorm-out ×50 | **是** `logits_finite` | 否 | **L2 class-hint**（≠S62/S86） | **高** | post-norm mag blowup；`!!!!` |
| S88 | residual-post negate | **是** `logits_finite` | 否 | **L2 class-hint**（≠S48/S86） | **高** | post residual polarity；`!!!!` |
| S89 | RMSNorm-out ÷50 | **是** `token_repeat` | 否 | **L2 class-hint**（≠S87/S78） | **高** | post-norm mag low |
| S90 | residual-post ×50 | **是** `logits_finite` | 否 | **L2 class-hint**（≠S55/S64/S88） | **高** | post residual mag；`!!!!` |
| S91 | residual-post ÷50 | **是** `token_repeat` | 否 | **L2 class-hint**（≠S90/S64/S88） | **高** | post residual mag low |
| S92 | temp-skip | **是** `token_repeat` | 否 | **L2 class-hint**（≠S36/S85） | **高** | precision=0 + detect≈47；unique rambling |
| S93 | residual←normed-x | **是** `token_repeat` | 否 | **L2 class-hint**（≠S31/S94/S88–S91） | **高** | residual wiring；`[it` repeat |
| S94 | residual↔x swap | **是** `logits_finite` | 否 | **L2 class-hint**（≠S31/S93/S88） | **高** | stream tuple swap；`!!!!` |
| S95 | temp-double | **是** `token_repeat` | 否 | **L2 class-hint**（≠S36/S85/S92） | **高** | apply_temperature×2；T>0 |
| S96 | RMSNorm-weight=ones | **是** `token_repeat` | 否 | **L2 class-hint**（≠S66/S71/S74） | **高** | precision=0 + detect=33；not GAP |
| S97 | residual-leak-add | **是** `logits_finite` | 否 | **L2 class-hint**（≠S31/S93/S94/S88–S91） | **高** | post-norm x+=residual；`!!!!` |
| S98 | min_p-skip | **是** `token_repeat` | 否 | **L2 class-hint**（≠S36/S85/S92/S95/S46） | **高** | precision=0 + detect=48；not GAP |
| S99 | top_p-skip | **是** `token_repeat` | 否 | **L2 class-hint**（≠S45/S98/temp） | **高** | precision=0 + detect=45；not GAP |
| S100 | RMSNorm-bias=weight | **是** `token_repeat` | 否 | **L2 class-hint**（≠S66/S71/S74/S96） | **高** | wrong bias wiring；异地×N |
| S101 | cos/sin-half-swap | **是** `token_repeat` | 否 | **L2 class-hint**（≠S42/S79–S82/S40/S25/S28） | **高** | rope phase halves；`111…` |
| S102 | RMSNorm-out-abs | **是** `token_repeat` | 否 | **L2 class-hint**（≠S86/S87–S89） | **高** | destroy signed post-norm |
| S103 | SwiGLU-gate-only | **是** `token_repeat` | 否 | **L2 class-hint**（≠S39/S50/S56–S81） | **高** | precision=0 + detect=48；not GAP |
| S104 | rope-skip-key | **是** `token_repeat` | 否 | **L2 class-hint**（≠S40/S25/S28/S101） | **高** | Q rotate / K skip；`One.` |
| S105 | rope-skip-query | **是** `token_repeat` | 否 | **L2 class-hint**（≠S104/S40/S25/S28/S101） | **高** | K rotate / Q skip；对偶 S104 |
| S106 | residual-post-abs | **是** `token_repeat` | 否 | **L2 class-hint**（≠S88/S90–S91/S102） | **高** | unsigned residual；precision=22 |
| S107 | SwiGLU-up-only | **是** `token_repeat` | 否 | **L2 class-hint**（≠S103/S39/S50） | **高** | up half only；≠ gate-only |
| S108 | hidden-abs | **是** `token_repeat` | 否 | **L2 class-hint**（≠S61/S75） | **高** | unsigned pre-head hidden |
| S109 | value-abs | **是** `token_repeat` | 否 | **L2 class-hint**（≠S58/S51） | **高** | precision=0 + detect=24；not GAP |
| S110 | RMSNorm-weight-abs | **是** `token_repeat` | 否 | **L2 class-hint**（≠S66/S71/S74/S96/S100） | **高** | unsigned norm weight |
| S111 | key-abs | **是** `token_repeat` | 否 | **L2 class-hint**（≠S54/S59/S109） | **高** | unsigned K；precision=30 |
| S112 | embed-abs | **是** `token_repeat` | 否 | **L2 class-hint**（≠S69/S43/S80） | **高** | unsigned embed；detect=46 |
| S113 | cos/sin-abs | **是** `token_repeat` | 否 | **L2 class-hint**（≠S42/S79–S82/S101/S40） | **高** | precision=0 + detect=48；not GAP |
| S114 | query-abs | **是** `token_repeat` | 否 | **L2 class-hint**（≠S52/S60/S109/S111） | **高** | unsigned Q；completes Q/K/V abs |
| S115 | SwiGLU-out-abs | **是** `token_repeat` | 否 | **L2 class-hint**（≠S67/S72/S103/S107） | **高** | unsigned SwiGLU out |
| S116 | RMSNorm-x-abs | **是** `token_repeat` | 否 | **L2 class-hint**（≠S73/S62/S78/S102） | **高** | unsigned pre-norm x；`pl` |
| S117 | query÷50 | **是** `token_repeat` | 否 | **L2 class-hint**（≠S60/S52/S114） | **高** | wrong Q mag low；digit repeat |
| S118 | key÷50 | **是** `token_repeat` | 否 | **L2 class-hint**（≠S59/S54/S111） | **高** | wrong K mag low；digit repeat |
| S119 | residual-pre-abs | **是** `token_repeat` | 否 | **L2 class-hint**（≠S48/S55/S64/S106） | **高** | unsigned pre-residual；servlet mix |
| S120 | RMSNorm-weight=zeros | **是** `token_repeat` | 否 | **L2 class-hint**（≠S96/S66/S71/S74/S110） | **高** | collapsed norm weight；`!!!!` |
| S121 | SwiGLU-input-abs | **是** `token_repeat` | 否 | **L2 class-hint**（≠S56/S76/S81/S115） | **高** | unsigned SwiGLU in；**precision=0 OK** |
| S122 | logits-abs | **是** `token_repeat` | 否 | **L2 class-hint**（≠S53/S65/S108） | **高** | unsigned logits；digit repeat |
| S123 | RMSNorm-bias=-weight | **是** `token_repeat` | 否 | **L2 class-hint**（≠S100/S66/S120） | **高** | wrong bias polarity；`.ON` |
| S124 | penalty-skip | **是** `token_repeat` | 否 | **L2 class-hint**（≠S46/S98/S99） | **高** | ignored penalties；**precision=0 OK** |
| S125 | residual-leak-sub | **是** `logits_finite` | 否 | **L2 class-hint**（≠S97/S93/S94/S31） | **高** | x=x-residual；`!!!!` |
| S126 | hidden-zeros | **是** `token_repeat` | 否 | **L2 class-hint**（≠S61/S75/S108/S122） | **高** | collapsed hidden；`!!!!` |
| S127 | embed-zeros | **是** `token_repeat` | 否 | **L2 class-hint**（≠S69/S43/S80/S112） | **高** | collapsed embed；`!!!!` |
| S128 | cos/sin-zeros | **是** `token_repeat` | 否 | **L2 class-hint**（≠S42/S79–S82/S101/S113） | **高** | collapsed rope phase |
| S129 | residual-pre-zeros | **是** `token_repeat` | 否 | **L2 class-hint**（≠S48/S55/S64/S119） | **高** | collapsed pre-residual；FieldType |
| S130 | query-zeros | **是** `token_repeat` | 否 | **L2 class-hint**（≠S60/S52/S114/S117） | **高** | collapsed Q |
| S131 | SwiGLU-out-zeros | **是** `token_repeat` | 否 | **L2 class-hint**（≠S67/S72/S115/S103/S107） | **高** | collapsed SwiGLU out |
| S132 | key-zeros | **是** `token_repeat` | 否 | **L2 class-hint**（≠S54/S59/S111/S118） | **高** | collapsed K |
| S133 | SwiGLU-input-zeros | **是** `token_repeat` | 否 | **L2 class-hint**（≠S56/S76/S81/S121/S131） | **高** | collapsed SwiGLU in |
| S134 | cos/sin-ones | **是** `token_repeat` | 否 | **L2 class-hint**（≠S42/S79–S82/S101/S113/S128） | **高** | unit rope phase |
| S135 | residual-post-zeros | **是** `token_repeat` | 否 | **L2 class-hint**（≠S88/S90/S91/S106/S129） | **高** | collapsed post-residual；FieldType |
| S136 | RMSNorm-out-zeros | **是** `token_repeat` | 否 | **L2 class-hint**（≠S86/S87/S89/S102） | **高** | collapsed post-norm x；`!!!!` |
| S137 | embed-ones | **是** `token_repeat` | 否 | **L2 class-hint**（≠S69/S43/S80/S112/S127） | **高** | unit embed；`××` |
| S138 | hidden-ones | **是** `token_repeat` | 否 | **L2 class-hint**（≠S61/S75/S108/S126） | **高** | unit pre-head hidden；`pl` |
| S139 | positions-ones | **是** `token_repeat` | 否 | **L2 class-hint**（≠S37/S57/S84） | **高** | pos→1；digits/`Friday`；precision 37 |
| S140 | residual-pre-ones | **是** `token_repeat` | 否 | **L2 class-hint**（≠S48/S55/S64/S119/S129） | **高** | unit pre-residual；`[code` |
| S141 | query-ones | **是** `token_repeat` | 否 | **L2 class-hint**（≠S60/S52/S114/S117/S130） | **高** | unit Q；`,`/`one of`；precision 36 |
| S142 | key-ones | **是** `token_repeat` | 否 | **L2 class-hint**（≠S54/S59/S111/S118/S132） | **高** | unit K；`,`/`and the`；precision 28 |
| S143 | SwiGLU-out-ones | **是** `token_repeat` | 否 | **L2 class-hint**（≠S67/S72/S115/S131） | **高** | unit SwiGLU out；`造假` |
| S144 | residual-post-ones | **是** `token_repeat` | 否 | **L2 class-hint**（≠S88/S90/S91/S106/S135） | **高** | unit post-residual；`[code` |
| S145 | RMSNorm-out-ones | **是** `token_repeat` | 否 | **L2 class-hint**（≠S86/S87/S89/S102/S136） | **高** | unit post-norm x；`pl` |
| S146 | SwiGLU-input-ones | **是** `token_repeat` | 否 | **L2 class-hint**（≠S56/S76/S81/S121/S133） | **高** | unit SwiGLU input；`造假` |
| S147 | positions-zeros | **是** `token_repeat` | 否 | **L2 class-hint**（≠S139/S57/S84） | **高** | pos→0；detect 47；precision 42 |
| S148 | value-ones | **是** `token_repeat` | 否 | **L2 class-hint**（≠S58/S51/S109） | **高** | unit V；`ior`；precision 30 |
| S149 | attn-out-ones | **是** `token_repeat` | 否 | **L2 class-hint**（≠S63/S41/S83） | **高** | unit attn-out；`ior`；precision 30 |

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

### S69 — Embed negate（≠ S43）

| 项 | 内容 |
|----|------|
| **三层率** | **16 / 26 / 48**；**`logits_finite`×48**；identical `!!!!` |
| **能否检测** | **是**（主=`logits_finite`） |
| **Skills 最远** | **L2**（wrong embed polarity）；≠ S43 ×100 |
| **有用度** | **高** |
| **待改进** | 无 |

### S70 — Variance eps ×1000（≠ S26/S38/S66）

| 项 | 内容 |
|----|------|
| **三层率** | **100 / 17 / 48**；`token_repeat`×48（slim） |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong norm eps）；≠ S26/S38/S66 |
| **有用度** | **高** |
| **待改进** | 无 |

### S71 — RMSNorm weight ×50（≠ S66）

| 项 | 内容 |
|----|------|
| **三层率** | **102 / 48 / 48**；**`logits_finite`×48**；identical `!!!!` |
| **能否检测** | **是**（主=`logits_finite`） |
| **Skills 最远** | **L2**（wrong norm-weight mag）；≠ S66 negate |
| **有用度** | **高** |
| **待改进** | 无 |

### S72 — SwiGLU out ×50（≠ S39/S50/S56/S67）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 48 / 48**；**`logits_finite`×48**；identical `!!!!` |
| **能否检测** | **是**（主=`logits_finite`） |
| **Skills 最远** | **L2**（wrong SwiGLU out mag）；≠ S39/S50/S56/S67 |
| **有用度** | **高** |
| **待改进** | 无 |

### S73 — RMSNorm x negate（≠ S48/S62）

| 项 | 内容 |
|----|------|
| **三层率** | **100 / 48 / 48**；**`logits_finite`×48**；identical `!!!!` |
| **能否检测** | **是**（主=`logits_finite`） |
| **Skills 最远** | **L2**（wrong pre-norm act polarity）；≠ S48/S62 |
| **有用度** | **高** |
| **待改进** | 无 |

### S74 — RMSNorm weight ÷50（≠ S66/S71）

| 项 | 内容 |
|----|------|
| **三层率** | **100 / 48 / 48**；`token_repeat`×48（slim） |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong norm-weight mag low）；≠ S66 negate ≠ S71 ×50 |
| **有用度** | **高** |
| **待改进** | 无 |

### S75 — Hidden ÷50（≠ S61/S53/S65）

| 项 | 内容 |
|----|------|
| **三层率** | **16 / 16 / 48**；`token_repeat`×48（slim） |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong pre-head hidden mag low）；≠ S61 ×50 ≠ S53/S65 logits |
| **有用度** | **高** |
| **待改进** | 无 |

### S76 — SwiGLU input ×50（≠ S39/S50/S56/S67/S72）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 48 / 48**；**`logits_finite`×48**；identical `!!!!` |
| **能否检测** | **是**（主=`logits_finite`） |
| **Skills 最远** | **L2**（wrong SwiGLU input mag）；≠ S39/S50/S56/S67/S72 |
| **有用度** | **高** |
| **待改进** | 无 |

### S77 — Variance eps ÷1000（≠ S70）

| 项 | 内容 |
|----|------|
| **三层率** | **100 / 16 / 48**；`token_repeat`×48（slim） |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong norm eps low）；≠ S70 ×1000 |
| **有用度** | **高** |
| **待改进** | 无 |

### S78 — RMSNorm x ÷50（≠ S62/S73）

| 项 | 内容 |
|----|------|
| **三层率** | **100 / 38 / 48**；`token_repeat`×48（slim） |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong pre-norm act mag low）；≠ S62 ×50 ≠ S73 negate |
| **有用度** | **高** |
| **待改进** | 无 |

### S79 — Cos/sin ×50（≠ S37/S40/S42/S25/S28）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 22 / 48**；`token_repeat`×48（slim） |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong rope phase mag）；≠ S37/S40/S42/S25/S28 |
| **有用度** | **高** |
| **待改进** | 无 |

### S80 — Embed ÷50（≠ S43/S69）

| 项 | 内容 |
|----|------|
| **三层率** | **16 / 17 / 33**；`token_repeat`×33（slim；detect < n_req） |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong embed mag low）；≠ S43 ×100 ≠ S69 negate |
| **有用度** | **高** |
| **待改进** | 无 |

### S81 — SwiGLU input ÷50（≠ S39/S50/S56/S76）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 48 / 48**；`token_repeat`×48（slim） |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong SwiGLU input mag low）；≠ S39/S50/S56 ≠ S76 ×50 |
| **有用度** | **高** |
| **待改进** | 无 |

### S82 — Cos/sin ÷50（≠ S37/S40/S42/S79）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 27 / 48**；`token_repeat`×48（slim） |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong rope phase mag low）；≠ S37/S40/S42 ≠ S79 ×50 |
| **有用度** | **高** |
| **待改进** | 无 |

### S83 — Attn-out ×50（≠ S41/S63）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 48 / 48**；`token_repeat`×48（slim） |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong attn-out mag mild）；≠ S41 ×1000 ≠ S63 negate |
| **有用度** | **高** |
| **待改进** | 无 |

### S84 — Positions ÷2（≠ S37/S57）

| 项 | 内容 |
|----|------|
| **三层率** | **132 / 44 / 48**；`token_repeat`×48（slim） |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong pos mag low）；≠ S37 pos-zero ≠ S57 ×2 |
| **有用度** | **高** |
| **待改进** | 无 |

### S85 — Temp ÷50（≠ S36）

| 项 | 内容 |
|----|------|
| **三层率** | **132 / 15 / 48**；`token_repeat`×48（slim；T=0.8） |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong T scale low）；≠ S36 post-temp÷50 |
| **有用度** | **高** |
| **待改进** | 无 |

### S86 — RMSNorm-out negate（≠ S73/S66）

| 项 | 内容 |
|----|------|
| **三层率** | **100 / 48 / 48**；**`logits_finite`×48**；identical `!!!!` |
| **能否检测** | **是**（主=`logits_finite`） |
| **Skills 最远** | **L2**（wrong post-norm polarity）；≠ S73 pre-norm ≠ S66 weight |
| **有用度** | **高** |
| **待改进** | 无 |

### S87 — RMSNorm-out ×50（≠ S62/S86）

| 项 | 内容 |
|----|------|
| **三层率** | **100 / 48 / 48**；**`logits_finite`×48**；identical `!!!!` |
| **能否检测** | **是**（主=`logits_finite`） |
| **Skills 最远** | **L2**（wrong post-norm mag）；≠ S62 pre×50 ≠ S86 out-neg |
| **有用度** | **高** |
| **待改进** | 无 |

### S88 — Residual-post negate（≠ S48/S86）

| 项 | 内容 |
|----|------|
| **三层率** | **100 / 48 / 48**；**`logits_finite`×48**；identical `!!!!` |
| **能否检测** | **是**（主=`logits_finite`） |
| **Skills 最远** | **L2**（wrong post-residual polarity）；≠ S48 pre ≠ S86 out |
| **有用度** | **高** |
| **待改进** | 无 |

### S89 — RMSNorm-out ÷50（≠ S87/S78）

| 项 | 内容 |
|----|------|
| **三层率** | **100 / 48 / 48**；`token_repeat`×48（slim） |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong post-norm mag low）；≠ S87 ×50 ≠ S78 pre÷50 |
| **有用度** | **高** |
| **待改进** | 无 |

### S90 — Residual-post ×50（≠ S55/S64/S88）

| 项 | 内容 |
|----|------|
| **三层率** | **102 / 48 / 48**；**`logits_finite`×48**；identical `!!!!` |
| **能否检测** | **是**（主=`logits_finite`） |
| **Skills 最远** | **L2**（wrong post-residual mag）；≠ S55/S64/S88 |
| **有用度** | **高** |
| **待改进** | 无 |

### S91 — Residual-post ÷50（≠ S90/S64/S88）

| 项 | 内容 |
|----|------|
| **三层率** | **100 / 48 / 48**；`token_repeat`×48（slim） |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong post-residual mag low）；≠ S90/S64/S88 |
| **有用度** | **高** |
| **待改进** | 无 |

### S92 — Temp-skip（≠ S36/S85）

| 项 | 内容 |
|----|------|
| **三层率** | **132 / 0 / 47**；`token_repeat`×47；T=0.8 |
| **能否检测** | **是**（47/48） |
| **Skills 最远** | **L2**（requested T ignored）；≠ S36/S85；**identical precision=0 is expected**（unique rambling）— not GAP |
| **有用度** | **高** |
| **待改进** | 无 |

### S93 — Residual←normed-x（≠ S31/S94/S88–S91）

| 项 | 内容 |
|----|------|
| **三层率** | **100 / 48 / 48**；`token_repeat`×48（slim） |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong residual wiring：residual=normed x）；≠ S31/S94/S88–S91 |
| **有用度** | **高** |
| **待改进** | 无 |

### S94 — Residual↔x swap（≠ S31/S93/S88）

| 项 | 内容 |
|----|------|
| **三层率** | **100 / 48 / 48**；**`logits_finite`×48**；identical `!!!!` |
| **能否检测** | **是**（主=`logits_finite`） |
| **Skills 最远** | **L2**（wrong stream wiring：tuple swap）；≠ S31/S93/S88 |
| **有用度** | **高** |
| **待改进** | 无 |

### S95 — Temp-double（≠ S36/S85/S92）

| 项 | 内容 |
|----|------|
| **三层率** | **132 / 9 / 48**；`token_repeat`×48；T=0.8 |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（T applied twice）；≠ S36/S85/S92 |
| **有用度** | **高** |
| **待改进** | 无 |

### S96 — RMSNorm-weight=ones（≠ S66/S71/S74）

| 项 | 内容 |
|----|------|
| **三层率** | **100 / 0 / 33**；`token_repeat`×33 |
| **能否检测** | **是**（33/48） |
| **Skills 最远** | **L2**（identity norm weight）；≠ S66/S71/S74；**identical precision=0 expected** — not GAP |
| **有用度** | **高** |
| **待改进** | 无 |

### S97 — Residual-leak-add（≠ S31/S93/S94/S88–S91）

| 项 | 内容 |
|----|------|
| **三层率** | **100 / 48 / 48**；**`logits_finite`×48**；identical `!!!!` |
| **能否检测** | **是**（主=`logits_finite`） |
| **Skills 最远** | **L2**（post-norm residual leak）；≠ S31/S93/S94/S88–S91 |
| **有用度** | **高** |
| **待改进** | 无 |

### S98 — Min_p-skip（≠ S36/S85/S92/S95/S46）

| 项 | 内容 |
|----|------|
| **三层率** | **132 / 0 / 48**；`token_repeat`×48；T=0.8 min_p=0.1 |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（requested min_p ignored）；≠ S36/S85/S92/S95/S46；**precision=0 expected** — not GAP |
| **有用度** | **高** |
| **待改进** | 无 |

### S99 — Top_p-skip（≠ S45/S98/temp）

| 项 | 内容 |
|----|------|
| **三层率** | **132 / 0 / 45**；`token_repeat`×45；T=0.8 top_p=0.9 |
| **能否检测** | **是**（45/48） |
| **Skills 最远** | **L2**（requested nucleus/k ignored）；≠ S45/S98/temp；**identical precision=0 expected** — not GAP |
| **有用度** | **高** |
| **待改进** | 无 |

### S100 — RMSNorm-bias=weight（≠ S66/S71/S74/S96）

| 项 | 内容 |
|----|------|
| **三层率** | **100 / 48 / 48**；`token_repeat`×48（slim） |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong norm bias wiring）；≠ S66/S71/S74/S96 |
| **有用度** | **高** |
| **待改进** | 无 |

### S101 — Cos/sin-half-swap（≠ S42/S79–S82/S40/S25/S28）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 48 / 48**；`token_repeat`×48；identical `111…` |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong rope phase halves）；≠ S42/S79–S82/S40/S25/S28 |
| **有用度** | **高** |
| **待改进** | 无 |

### S102 — RMSNorm-out-abs（≠ S86/S87–S89）

| 项 | 内容 |
|----|------|
| **三层率** | **100 / 48 / 48**；`token_repeat`×48（slim） |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（destroy signed post-norm act）；≠ S86/S87–S89 |
| **有用度** | **高** |
| **待改进** | 无 |

### S103 — SwiGLU-gate-only（≠ S39/S50/S56–S81）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 0 / 48**；`token_repeat`×48 |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（incomplete SwiGLU：gate only）；≠ S39/S50/S56–S81；**identical precision=0 expected** — not GAP |
| **有用度** | **高** |
| **待改进** | 无 |

### S104 — Rope-skip-key（≠ S40/S25/S28/S101）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 48 / 48**；`token_repeat`×48；identical `One.` |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（Q/K RoPE phase mismatch）；≠ S40/S25/S28/S101 |
| **有用度** | **高** |
| **待改进** | 无 |

### S105 — Rope-skip-query（≠ S104/S40/S25/S28/S101）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 48 / 48**；`token_repeat`×48 |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（Q/K RoPE phase mismatch，对偶 S104）；≠ S104/S40/S25/S28/S101 |
| **有用度** | **高** |
| **待改进** | 无 |

### S106 — Residual-post-abs（≠ S88/S90–S91/S102）

| 项 | 内容 |
|----|------|
| **三层率** | **100 / 22 / 48**；`token_repeat`×48 |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（unsigned post-residual）；≠ S88/S90–S91/S102 |
| **有用度** | **高** |
| **待改进** | 无 |

### S107 — SwiGLU-up-only（≠ S103/S39/S50）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 48 / 48**；`token_repeat`×48 |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（incomplete SwiGLU：up only）；≠ S103/S39/S50 |
| **有用度** | **高** |
| **待改进** | 无 |

### S108 — Hidden-abs（≠ S61/S75）

| 项 | 内容 |
|----|------|
| **三层率** | **16 / 48 / 48**；`token_repeat`×48 |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（unsigned pre-head hidden）；≠ S61/S75 |
| **有用度** | **高** |
| **待改进** | 无 |

### S109 — Value-abs（≠ S58/S51）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 0 / 24**；`token_repeat`×24 |
| **能否检测** | **是**（24/48） |
| **Skills 最远** | **L2**（unsigned V）；≠ S58/S51；**identical precision=0 expected** — not GAP |
| **有用度** | **高** |
| **待改进** | 无 |

### S110 — RMSNorm-weight-abs（≠ S66/S71/S74/S96/S100）

| 项 | 内容 |
|----|------|
| **三层率** | **100 / 19 / 48**；`token_repeat`×48 |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（unsigned norm weight）；≠ S66/S71/S74/S96/S100 |
| **有用度** | **高** |
| **待改进** | 无 |

### S111 — Key-abs（≠ S54/S59/S109）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 30 / 48**；`token_repeat`×48 |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（unsigned K）；≠ S54/S59/S109 |
| **有用度** | **高** |
| **待改进** | 无 |

### S112 — Embed-abs（≠ S69/S43/S80）

| 项 | 内容 |
|----|------|
| **三层率** | **16 / 34 / 46**；`token_repeat`×46 |
| **能否检测** | **是**（46/48） |
| **Skills 最远** | **L2**（unsigned embed）；≠ S69/S43/S80 |
| **有用度** | **高** |
| **待改进** | 无 |

### S113 — Cos/sin-abs（≠ S42/S79–S82/S101/S40）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 0 / 48**；`token_repeat`×48 |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（unsigned rope phase）；≠ S42/S79–S82/S101/S40；**identical precision=0 expected** — not GAP |
| **有用度** | **高** |
| **待改进** | 无 |

### S114 — Query-abs（≠ S52/S60/S109/S111）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 47 / 48**；`token_repeat`×48 |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（unsigned Q）；≠ S52/S60/S109/S111 |
| **有用度** | **高** |
| **待改进** | 无 |

### S115 — SwiGLU-out-abs（≠ S67/S72/S103/S107）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 29 / 48**；`token_repeat`×48 |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（unsigned SwiGLU out）；≠ S67/S72/S103/S107 |
| **有用度** | **高** |
| **待改进** | 无 |

### S116 — RMSNorm-x-abs（≠ S73/S62/S78/S102）

| 项 | 内容 |
|----|------|
| **三层率** | **100 / 48 / 48**；`token_repeat`×48；identical `pl` |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（unsigned pre-norm x）；≠ S73/S62/S78/S102 |
| **有用度** | **高** |
| **待改进** | 无 |

### S117 — Query-scale-down（≠ S60/S52/S114）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 34 / 48**；`token_repeat`×48 |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong Q magnitude low）；≠ S60/S52/S114 |
| **有用度** | **高** |
| **待改进** | 无 |

### S118 — Key-scale-down（≠ S59/S54/S111）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 33 / 48**；`token_repeat`×48 |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong K magnitude low）；≠ S59/S54/S111 |
| **有用度** | **高** |
| **待改进** | 无 |

### S119 — Residual-pre-abs（≠ S48/S55/S64/S106）

| 项 | 内容 |
|----|------|
| **三层率** | **102 / 41 / 48**；`token_repeat`×48；mixed-script servlet |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（unsigned pre-residual）；≠ S48/S55/S64/S106 |
| **有用度** | **高** |
| **待改进** | 无 |


### S120 — RMSNorm-weight=zeros（≠ S96/S66/S71/S74/S110）

| 项 | 内容 |
|----|------|
| **三层率** | **100 / 48 / 48**；`token_repeat`×48；identical `!!!!` |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（collapsed norm weight）；≠ S96/S66/S71/S74/S110 |
| **有用度** | **高** |
| **待改进** | 无 |

### S121 — SwiGLU-input-abs（≠ S56/S76/S81/S115；precision=0 OK）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 0 / 48**；`token_repeat`×48；unique mixed-script |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（unsigned SwiGLU input）；≠ S56/S76/S81/S115；**identical precision=0 expected** — not GAP |
| **有用度** | **高** |
| **待改进** | 无 |

### S122 — Logits-abs（≠ S53/S65/S108）

| 项 | 内容 |
|----|------|
| **三层率** | **16 / 16 / 48**；`token_repeat`×48 |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（unsigned logits）；≠ S53/S65/S108 |
| **有用度** | **高** |
| **待改进** | 无 |



### S123 — RMSNorm-bias=-weight（≠ S100/S66/S120）

| 项 | 内容 |
|----|------|
| **三层率** | **100 / 33 / 48**；`token_repeat`×48 |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong norm bias polarity）；≠ S100/S66/S120 |
| **有用度** | **高** |
| **待改进** | 无 |

### S124 — Penalty-skip（≠ S46/S98/S99；precision=0 OK）

| 项 | 内容 |
|----|------|
| **三层率** | **132 / 0 / 48**；`token_repeat`×48；unique id-echo；T>0 |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（ignored penalties）；≠ S46/S98/S99；**identical precision=0 expected** — not GAP |
| **有用度** | **高** |
| **待改进** | 无 |

### S125 — Residual-leak-sub（≠ S97/S93/S94/S31）

| 项 | 内容 |
|----|------|
| **三层率** | **100 / 48 / 48**；`logits_finite`×48；identical `!!!!` |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（wrong residual recombine：sub）；≠ S97/S93/S94/S31 |
| **有用度** | **高** |
| **待改进** | 无 |



### S126 — Hidden-zeros（≠ S61/S75/S108/S122）

| 项 | 内容 |
|----|------|
| **三层率** | **16 / 48 / 48**；`token_repeat`×48；identical `!!!!` |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（collapsed pre-head hidden）；≠ S61/S75/S108/S122 |
| **有用度** | **高** |
| **待改进** | 无 |

### S127 — Embed-zeros（≠ S69/S43/S80/S112）

| 项 | 内容 |
|----|------|
| **三层率** | **16 / 48 / 48**；`token_repeat`×48；identical `!!!!` |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（collapsed embed）；≠ S69/S43/S80/S112 |
| **有用度** | **高** |
| **待改进** | 无 |

### S128 — Cos/sin-zeros（≠ S42/S79–S82/S101/S113）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 28 / 48**；`token_repeat`×48 |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（collapsed rope phase）；≠ S42/S79–S82/S101/S113 |
| **有用度** | **高** |
| **待改进** | 无 |


### S129 — Residual-pre-zeros（≠ S48/S55/S64/S119）

| 项 | 内容 |
|----|------|
| **三层率** | **100 / 48 / 48**；`token_repeat`×48；identical `FieldType` |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（collapsed pre-residual）；≠ S48/S55/S64/S119 |
| **有用度** | **高** |
| **待改进** | 无 |

### S130 — Query-zeros（≠ S60/S52/S114/S117）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 28 / 48**；`token_repeat`×48 |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（collapsed Q）；≠ S60/S52/S114/S117 |
| **有用度** | **高** |
| **待改进** | 无 |

### S131 — SwiGLU-out-zeros（≠ S67/S72/S115/S103/S107）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 48 / 48**；`token_repeat`×48 |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（collapsed SwiGLU out）；≠ S67/S72/S115/S103/S107 |
| **有用度** | **高** |
| **待改进** | 无 |


### S132 — Key-zeros（≠ S54/S59/S111/S118）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 28 / 48**；`token_repeat`×48 |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（collapsed K）；≠ S54/S59/S111/S118 |
| **有用度** | **高** |
| **待改进** | 无 |

### S133 — SwiGLU-input-zeros（≠ S56/S76/S81/S121/S131）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 48 / 48**；`token_repeat`×48 |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（collapsed SwiGLU input）；≠ S56/S76/S81/S121/S131 |
| **有用度** | **高** |
| **待改进** | 无 |

### S134 — Cos/sin-ones（≠ S42/S79–S82/S101/S113/S128）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 48 / 48**；`token_repeat`×48 |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（unit rope phase）；≠ S42/S79–S82/S101/S113/S128 |
| **有用度** | **高** |
| **待改进** | 无 |


### S135 — Residual-post-zeros（≠ S88/S90/S91/S106/S129）

| 项 | 内容 |
|----|------|
| **三层率** | **102 / 48 / 48**；`token_repeat`×48；identical `FieldType` |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（collapsed post-residual）；≠ S88/S90/S91/S106/S129 |
| **有用度** | **高** |
| **待改进** | 无 |

### S136 — RMSNorm-out-zeros（≠ S86/S87/S89/S102）

| 项 | 内容 |
|----|------|
| **三层率** | **100 / 48 / 48**；`token_repeat`×48；identical `!!!!` |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（collapsed post-norm x）；≠ S86/S87/S89/S102 |
| **有用度** | **高** |
| **待改进** | 无 |

### S137 — Embed-ones（≠ S69/S43/S80/S112/S127）

| 项 | 内容 |
|----|------|
| **三层率** | **16 / 48 / 48**；`token_repeat`×48；identical `××` |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（unit embed）；≠ S69/S43/S80/S112/S127 |
| **有用度** | **高** |
| **待改进** | 无 |

### S138 — Hidden-ones（≠ S61/S75/S108/S126）

| 项 | 内容 |
|----|------|
| **三层率** | **16 / 48 / 48**；`token_repeat`×48；identical `pl` |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（unit pre-head hidden）；≠ S61/S75/S108/S126 |
| **有用度** | **高** |
| **待改进** | 无 |

### S139 — Positions-ones（≠ S37/S57/S84）

| 项 | 内容 |
|----|------|
| **三层率** | **132 / 37 / 48**；`token_repeat`×48；digits/`Friday`；precision 37 OK |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（pos collapse to 1）；≠ S37/S57/S84 |
| **有用度** | **高** |
| **待改进** | 无 |

### S140 — Residual-pre-ones（≠ S48/S55/S64/S119/S129）

| 项 | 内容 |
|----|------|
| **三层率** | **102 / 48 / 48**；`token_repeat`×48；identical `[code` |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（unit pre-residual）；≠ S48/S55/S64/S119/S129 |
| **有用度** | **高** |
| **待改进** | 无 |

### S141 — Query-ones（≠ S60/S52/S114/S117/S130）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 36 / 48**；`token_repeat`×48；`,`/`one of`/空格；precision 36 OK |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（unit Q）；≠ S60/S52/S114/S117/S130 |
| **有用度** | **高** |
| **待改进** | 无 |

### S142 — Key-ones（≠ S54/S59/S111/S118/S132）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 28 / 48**；`token_repeat`×48；`,`/`and the`；precision 28 OK |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（unit K）；≠ S54/S59/S111/S118/S132 |
| **有用度** | **高** |
| **待改进** | 无 |

### S143 — SwiGLU-out-ones（≠ S67/S72/S115/S131）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 48 / 48**；`token_repeat`×48；identical `造假` |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（unit SwiGLU out）；≠ S67/S72/S115/S131 |
| **有用度** | **高** |
| **待改进** | 无 |

### S144 — Residual-post-ones（≠ S88/S90/S91/S106/S135）

| 项 | 内容 |
|----|------|
| **三层率** | **100 / 48 / 48**；`token_repeat`×48；identical `[code` |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（unit post-residual）；≠ S88/S90/S91/S106/S135 |
| **有用度** | **高** |
| **待改进** | 无 |

### S145 — RMSNorm-out-ones（≠ S86/S87/S89/S102/S136）

| 项 | 内容 |
|----|------|
| **三层率** | **100 / 48 / 48**；`token_repeat`×48；identical `pl` |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（unit post-norm x）；≠ S86/S87/S89/S102/S136 |
| **有用度** | **高** |
| **待改进** | 无 |

### S146 — SwiGLU-input-ones（≠ S56/S76/S81/S121/S133）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 48 / 48**；`token_repeat`×48；identical `造假` |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（unit SwiGLU input）；≠ S56/S76/S81/S121/S133 |
| **有用度** | **高** |
| **待改进** | 无 |

### S147 — Positions-zeros（≠ S139/S57/S84）

| 项 | 内容 |
|----|------|
| **三层率** | **132 / 42 / 47**；`token_repeat`×47；digit/`\``；detect 47 OK |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（pos collapse to 0）；≠ S139/S57/S84 |
| **有用度** | **高** |
| **待改进** | 无 |

### S148 — Value-ones（≠ S58/S51/S109）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 30 / 48**；`token_repeat`×48；identical `ior`；precision 30 OK |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（unit V）；≠ S58/S51/S109 |
| **有用度** | **高** |
| **待改进** | 无 |

### S149 — Attn-out-ones（≠ S63/S41/S83）

| 项 | 内容 |
|----|------|
| **三层率** | **58 / 30 / 48**；`token_repeat`×48；identical `ior`；precision 30 OK |
| **能否检测** | **是** |
| **Skills 最远** | **L2**（unit attn-out）；≠ S63/S41/S83 |
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
| **S69** | 无 embed-negate class → **L2** via **`logits_finite`**；≠ S43 | **是** |
| **S70** | 无 variance-eps class → **L2**；≠ S26/S38/S66 | **是** |
| **S71** | 无 RMSNorm-weight×50 class → **L2** via **`logits_finite`**；≠ S66 | **是** |
| **S72** | 无 SwiGLU-out×50 class → **L2** via **`logits_finite`**；≠ S39/S50/S56/S67 | **是** |
| **S73** | 无 RMSNorm-x-negate class → **L2** via **`logits_finite`**；≠ S48/S62 | **是** |
| **S74** | 无 RMSNorm-weight÷50 class → **L2**；≠ S66/S71 | **是** |
| **S75** | 无 hidden÷50 class → **L2**；≠ S61/S53/S65 | **是** |
| **S76** | 无 SwiGLU-input×50 class → **L2** via **`logits_finite`**；≠ S39/S50/S56/S67/S72 | **是** |
| **S77** | 无 variance-eps÷1000 class → **L2**；≠ S70 | **是** |
| **S78** | 无 RMSNorm-x÷50 class → **L2**；≠ S62/S73 | **是** |
| **S79** | 无 cos_sin×50 class → **L2**；≠ S37/S40/S42/S25/S28 | **是** |
| **S80** | 无 embed÷50 class → **L2**；≠ S43/S69 | **是** |
| **S81** | 无 SwiGLU-input÷50 class → **L2**；≠ S39/S50/S56/S76 | **是** |
| **S82** | 无 cos_sin÷50 class → **L2**；≠ S37/S40/S42/S79 | **是** |
| **S83** | 无 attn-out×50 class → **L2**；≠ S41/S63 | **是** |
| **S84** | 无 positions÷2 class → **L2**；≠ S37/S57 | **是** |
| **S85** | 无 temp÷50 class → **L2**；≠ S36 | **是** |
| **S86** | 无 RMSNorm-out-negate class → **L2** via **`logits_finite`**；≠ S73/S66 | **是** |
| **S87** | 无 RMSNorm-out×50 class → **L2** via **`logits_finite`**；≠ S62/S86 | **是** |
| **S88** | 无 residual-post-negate class → **L2** via **`logits_finite`**；≠ S48/S86 | **是** |
| **S89** | 无 RMSNorm-out÷50 class → **L2**；≠ S87/S78 | **是** |
| **S90** | 无 residual-post×50 class → **L2** via **`logits_finite`**；≠ S55/S64/S88 | **是** |
| **S91** | 无 residual-post÷50 class → **L2**；≠ S90/S64/S88 | **是** |
| **S92** | 无 temp-skip class → **L2**；≠ S36/S85；precision=0 + detect=47 PASS | **是** |
| **S93** | 无 residual←normed-x class → **L2**；≠ S31/S94/S88–S91 | **是** |
| **S94** | 无 residual↔x swap class → **L2** via **`logits_finite`**；≠ S31/S93/S88 | **是** |
| **S95** | 无 temp-double class → **L2**；≠ S36/S85/S92 | **是** |
| **S96** | 无 RMSNorm-weight=ones class → **L2**；≠ S66/S71/S74；precision=0 + detect=33 PASS | **是** |
| **S97** | 无 residual-leak-add class → **L2** via **`logits_finite`**；≠ S31/S93/S94/S88–S91 | **是** |
| **S98** | 无 min_p-skip class → **L2**；≠ S36/S85/S92/S95/S46；precision=0 + detect=48 PASS | **是** |
| **S99** | 无 top_p-skip class → **L2**；≠ S45/S98/temp；precision=0 + detect=45 PASS | **是** |
| **S100** | 无 RMSNorm-bias=weight class → **L2**；≠ S66/S71/S74/S96 | **是** |
| **S101** | 无 cos/sin-half-swap class → **L2**；≠ S42/S79–S82/S40/S25/S28 | **是** |
| **S102** | 无 RMSNorm-out-abs class → **L2**；≠ S86/S87–S89 | **是** |
| **S103** | 无 SwiGLU-gate-only class → **L2**；≠ S39/S50/S56–S81；precision=0 + detect=48 PASS | **是** |
| **S104** | 无 rope-skip-key class → **L2**；≠ S40/S25/S28/S101 | **是** |
| **S105** | 无 rope-skip-query class → **L2**；≠ S104/S40/S25/S28/S101 | **是** |
| **S106** | 无 residual-post-abs class → **L2**；≠ S88/S90–S91/S102 | **是** |
| **S107** | 无 SwiGLU-up-only class → **L2**；≠ S103/S39/S50 | **是** |
| **S108** | 无 hidden-abs class → **L2**；≠ S61/S75 | **是** |
| **S109** | 无 value-abs class → **L2**；≠ S58/S51；precision=0 + detect=24 PASS | **是** |
| **S110** | 无 RMSNorm-weight-abs class → **L2**；≠ S66/S71/S74/S96/S100 | **是** |
| **S111** | 无 key-abs class → **L2**；≠ S54/S59/S109 | **是** |
| **S112** | 无 embed-abs class → **L2**；≠ S69/S43/S80 | **是** |
| **S113** | 无 cos/sin-abs class → **L2**；≠ S42/S79–S82/S101/S40；precision=0 + detect=48 PASS | **是** |
| **S114** | 无 query-abs class → **L2**；≠ S52/S60/S109/S111 | **是** |
| **S115** | 无 SwiGLU-out-abs class → **L2**；≠ S67/S72/S103/S107 | **是** |
| **S116** | 无 RMSNorm-x-abs class → **L2**；≠ S73/S62/S78/S102 | **是** |
| **S117** | 无 query÷50 class → **L2**；≠ S60/S52/S114 | **是** |
| **S118** | 无 key÷50 class → **L2**；≠ S59/S54/S111 | **是** |
| **S119** | 无 residual-pre-abs class → **L2**；≠ S48/S55/S64/S106 | **是** |
| **S120** | 无 RMSNorm-weight=zeros class → **L2**；≠ S96/S66/S71/S74/S110 | **是** |
| **S121** | 无 SwiGLU-input-abs class → **L2**；≠ S56/S76/S81/S115；precision=0 + detect=48 PASS | **是** |
| **S122** | 无 logits-abs class → **L2**；≠ S53/S65/S108 | **是** |
| **S123** | 无 RMSNorm-bias=-weight class → **L2**；≠ S100/S66/S120 | **是** |
| **S124** | 无 penalty-skip class → **L2**；≠ S46/S98/S99；precision=0 + detect=48 PASS | **是** |
| **S125** | 无 residual-leak-sub class → **L2** via **`logits_finite`**；≠ S97/S93/S94/S31 | **是** |
| **S126** | 无 hidden-zeros class → **L2**；≠ S61/S75/S108/S122 | **是** |
| **S127** | 无 embed-zeros class → **L2**；≠ S69/S43/S80/S112 | **是** |
| **S128** | 无 cos/sin-zeros class → **L2**；≠ S42/S79–S82/S101/S113 | **是** |
| **S129** | 无 residual-pre-zeros class → **L2**；≠ S48/S55/S64/S119 | **是** |
| **S130** | 无 query-zeros class → **L2**；≠ S60/S52/S114/S117 | **是** |
| **S131** | 无 SwiGLU-out-zeros class → **L2**；≠ S67/S72/S115/S103/S107 | **是** |
| **S132** | 无 key-zeros class → **L2**；≠ S54/S59/S111/S118 | **是** |
| **S133** | 无 SwiGLU-input-zeros class → **L2**；≠ S56/S76/S81/S121/S131 | **是** |
| **S134** | 无 cos/sin-ones class → **L2**；≠ S42/S79–S82/S101/S113/S128 | **是** |
| **S135** | 无 residual-post-zeros class → **L2**；≠ S88/S90/S91/S106/S129 | **是** |
| **S136** | 无 RMSNorm-out-zeros class → **L2**；≠ S86/S87/S89/S102 | **是** |
| **S137** | 无 embed-ones class → **L2**；≠ S69/S43/S80/S112/S127 | **是** |
| **S138** | 无 hidden-ones class → **L2**；≠ S61/S75/S108/S126 | **是** |
| **S139** | 无 positions-ones class → **L2**；≠ S37/S57/S84 | **是** |
| **S140** | 无 residual-pre-ones class → **L2**；≠ S48/S55/S64/S119/S129 | **是** |
| **S141** | 无 query-ones class → **L2**；≠ S60/S52/S114/S117/S130 | **是** |
| **S142** | 无 key-ones class → **L2**；≠ S54/S59/S111/S118/S132 | **是** |
| **S143** | 无 SwiGLU-out-ones class → **L2**；≠ S67/S72/S115/S131 | **是** |
| **S144** | 无 residual-post-ones class → **L2**；≠ S88/S90/S91/S106/S135 | **是** |
| **S145** | 无 RMSNorm-out-ones class → **L2**；≠ S86/S87/S89/S102/S136 | **是** |
| **S146** | 无 SwiGLU-input-ones class → **L2**；≠ S56/S76/S81/S121/S133 | **是** |
| **S147** | 无 positions-zeros class → **L2**；≠ S139/S57/S84 | **是** |
| **S148** | 无 value-ones class → **L2**；≠ S58/S51/S109 | **是** |
| **S149** | 无 attn-out-ones class → **L2**；≠ S63/S41/S83 | **是** |

详见 [anomaly-skills-verify-loop-20261017.md](./anomaly-skills-verify-loop-20261017.md)。

## Skills 全局缺口（优先序）

1. **Garbled / identical-across / unique-garbage detector**（解锁 S01/S07/**S45** → 可升「高」有用度的 online 段）  
2. MoE/溢出类：**明确 L3 不可达**（避免空跑 ref）  
3. Spec 分布性：summarize 突出 `acceptance_rate`  
4. ~~Weight/Quant always-on 场景落地~~ → **S23/S24 PASS L1**（仍不可定位张量）  
5. KV PASS（S10′/S12/S30/S47）：标准 ref-kv 流水线模板 + 容器 dump_dir 重映射  
6. Soft-inv / cast / residual / graph-pad / softcap / attn / temp / pos / norm / act / rope / embed / penalty / kv-swap / **positions-zeros / value-ones / attn-out-ones**：**S25–S149 L2**（除 S44 INVALID / S45 FAIL+GAP）

---

## 如何续写本文

1. 160 在 handoff Inbox 追加一行 → skills 方拉 fail-evidence。  
2. 跑 `summarize_reports` / `score_completion_samples` /（可选）`verify_request_kv`。  
3. 在本文件「逐场景」追加一节 + 更新总表有用度。  
4. 新 class → 改 `analysis/skill/` 并 bump `SKILLS_METADATA` → `git push main`。  
5. 同步 AgentStore：`docs/anomaly-skills-capability-20261017.md` 与 `docs/anomaly-skills-runs/`。

**证据索引：** `tests/build-anomaly-env/fail-evidence/Sxx/` · 店内 `docs/anomaly-skills-runs/` · `docs/anomaly-skills-analysis-20261017.md`
