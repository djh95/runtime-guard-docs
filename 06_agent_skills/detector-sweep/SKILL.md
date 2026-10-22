---
name: runtime-guard-detector-sweep
description: >-
  Emit a minimal temporary runtime_config that enables all shipped
  runtime_guard detectors with on_trigger report only and dump off, for
  unclassified intermittent bugs. No thresholds, no dump_kv, no offline
  report parsing. After a hit, hand off to config-recommender.
---

# runtime_guard Detector Sweep（极简筛查）

**类型：原子 · 在线配置。** 只产出临时 sweep 模板；不做读盘、不做阈值调优。

手册：[01](../../01_enable_and_start/README.md) · [03](../../03_detectors/README.md) · 契约：[SKILLS_METADATA.md](./SKILLS_METADATA.md)

## When

偶发质量问题、类别未知 → 一次压测尽量让**已合入** detector 先分类（只 report）。

## 已合入（#16849）

| Key | 抓什么 |
|-----|--------|
| `token_repeat` | 局部复读 |
| `logits_finite` | 采样前 NaN/Inf |
| `spec_acceptance` | Spec 接受率/长度（**仅 MTP**；非 MTP 不要开） |

**勿启用：** `output_substring` / `token_logprob` / `slot_*` / `kv_state`。

**已知 sweep 盲区（仍跑 samples）：** 有限 mixed-script 垃圾、跨请求完全相同 completion（S07/S45 class；**S01 dense 为复现未出现，非本盲区**）——三键可能全空 report；压测后用 `score_completion_samples` 判 precision（排除 CJK 误标），有真实坏输出再标 GAP；不要把「无 report」当成「无异常」。

**数值溢出 / softcap（S20 class）：** sweep 开齐 `token_repeat`+`logits_finite`；塌缩成 `!!!!`/token0 时以 `token_repeat` 命中为准，勿因 `logits_finite` 空报就结案。

**Spec / eagle3（S22 class）：** 非 MTP 勿开 `spec_acceptance`；有 draft 时必须开。低接受率 + 正常文本仍算 precision（分布性），交给 analysis 读 report，勿只盯 samples。

**权重/量化 always-on（S23/S24）：** sweep 开 `token_repeat`（+可选 `logits_finite`）。命中后 **不要** 承诺定位参数；与 S07 FAIL+GAP 区分（S24 已可 detect）。

**RoPE / RMSNorm soft-inv（S25/S26/S28）：** 同样开 `token_repeat`。命中后交 analysis 做 **L2 class-hint**（half-drop / fp32-mul / neox→interleaved）；勿与 S11 MLA pad 混谈。

**Sampling cast / null-block KV / residual drop（S29/S30/S31）：** 开 `token_repeat`。S29≠S20；S30≠S01/S10；S31≠S26。S30 可兼 dump 供后续 L3。

**FIA FULL-graph pad / incomplete softcap（S32/S33）：** 开 `token_repeat`。S32 精度看 unique garbage（score `pad_echo`），勿因 identical-mode 低判「无 precision」。S33≠S20。

**Attn scale drop / causal-off（S34/S35）：** 开 `token_repeat`。S34 unique digit/junk（wrong attn temp）；S35 强 phrase/prompt-echo（future leak）。S34≠S20/S32/S33；S35≠S34。

**Temp blowup / pos-zero / RMSNorm skip（S36/S37/S38）：** S36/S37 开 `token_repeat`（S36 看 unique `id_echo`）。S38 **必须开 `logits_finite`**（主检出）；`!!!!` 可兼 `token_repeat` 对照。S36≠S29/S20；S37≠S25/S28；S38≠S26/S31/S20。

**SwiGLU skip / RoPE skip / attn-out ×1000（S39/S40/S41）：** S39/S41 **开 `logits_finite`**（主）；S40 开 `token_repeat`（phrase 复读）。S39≠S26/S31/S38；S40≠S25/S28/S37；S41≠S34/S14/S35。

**RoPE phase / embed scale（S42/S43）：** 开 `token_repeat`。S42≠S37/S40/S25/S28；S43 看 newline collapse。**S44 logits.zero_** 勿当 PASS（synthetic amplifier）。

**Penalty flip / K/V swap（S46/S47）：** 开 `token_repeat`。S46≠S45/S44；S47≠S34/S35/S41。**S45 top-k on -logits** → unique garbage **FAIL+GAP**（同 S07；≠ S01 dense）；勿放大器硬凑。

**Residual negate / attn×50 / SwiGLU half-swap（S48/S49/S50）：** S48/S50 **开 `logits_finite`**（主；`!!!!`）。S49 开 `token_repeat`（unique/`1.1.1…`）。S48≠S31/S38；S49≠S34/S41；S50≠S39。

**Value×50 / query-negate / logits÷50（S51/S52/S53）：** 开 `token_repeat`。S51≠S41/S47/S49；S52≠S47/S51/S42；S53≠S36/S44。

## 输出模板（可热更）

启动须已开 `runtime_config_hot_reload=true`（见 01）。Grep 确认 reload；失败会保留旧配置。

```jsonc
// 临时 sweep：只 report，禁止业务长期运行
{
  "dump": { "auto_max_times": 0, "manual_dump": false },
  "report": { "max_per_req": 1, "save_sensitive_info": true },
  "detector": {
    "token_repeat": { "enabled": true, "on_trigger": ["report"] },
    "logits_finite": { "enabled": true, "on_trigger": ["report"] },
    "spec_acceptance": { "enabled": true, "on_trigger": ["report"] }  // 仅 MTP
  }
}
```

允许的开关级字段：`enabled` / `on_trigger:["report"]` / dump 全关 / `max_per_req` / `save_sensitive_info`。

## forbidden

- window、阈值、`ignore_token_ids`、`auto_max_times>0`、cooldown、`dump_kv`  
- 解析本地 report/dump（→ `runtime-guard-analysis`）  
- 当作正式长期业务配置

## 后续

命中后 → `runtime-guard-config-recommender` 出正式阈值与（按需）dump 配额。  
读报告目录 → `analysis`。端到端编排 → `investigation`。

## Related

`config-recommender` · `analysis` · `investigation`

**Key-negate / residual×50 / SwiGLU-input-negate（S54/S55/S56）：** S54 开 `token_repeat`。S55/S56 **开 `logits_finite`**（主）。S54≠S47/S51/S52；S55≠S31/S38/S48；S56≠S39/S50。

**Positions×2 / value-negate / key×50（S57/S58/S59）：** S57/S59 开 `token_repeat`。S58 **开 `logits_finite`**（主）。S57≠S37；S58≠S51/S47/S52/S54；S59≠S49/S51/S54。

**Query×50 / hidden×50 / pre-norm x×50（S60/S61/S62）：** S60/S61 开 `token_repeat`。S62 **开 `logits_finite`**（主）。S60≠S52/S49/S51/S59；S61≠S53/S43；S62≠S26/S38/S48/S55。

**Attn-out-negate / residual÷50 / logits×50（S63/S64/S65）：** S63 **开 `logits_finite`**（主）。S64/S65 开 `token_repeat`。S63≠S41；S64≠S48/S55；S65≠S53/S36。

**RMSNorm-weight-negate / SwiGLU-out-negate / attn-scale÷50（S66/S67/S68）：** S66/S67 **开 `logits_finite`**（主）。S68 开 `token_repeat`。S66≠S26/S38/S48/S55/S62；S67≠S39/S50/S56；S68≠S34/S49。

**Embed-negate / variance-eps×1000 / RMSNorm-weight×50（S69/S70/S71）：** S69/S71 **开 `logits_finite`**（主）。S70 开 `token_repeat`。S69≠S43；S70≠S26/S38/S66；S71≠S66。

**SwiGLU-out×50 / RMSNorm-x-negate / RMSNorm-weight÷50（S72/S73/S74）：** S72/S73 **开 `logits_finite`**（主）。S74 开 `token_repeat`。S72≠S39/S50/S56/S67；S73≠S48/S62；S74≠S66/S71。

**Hidden÷50 / SwiGLU-input×50 / variance-eps÷1000（S75/S76/S77）：** S75/S77 开 `token_repeat`。S76 **开 `logits_finite`**（主）。S75≠S61/S53/S65；S76≠S39/S50/S56/S67/S72；S77≠S70。

**RMSNorm-x÷50 / cos_sin×50 / embed÷50（S78/S79/S80）：** 开 `token_repeat`。S78≠S62/S73；S79≠S37/S40/S42/S25/S28；S80≠S43/S69。

**SwiGLU-input÷50 / cos_sin÷50 / attn-out×50（S81/S82/S83）：** 开 `token_repeat`。S81≠S39/S50/S56/S76；S82≠S37/S40/S42/S79；S83≠S41/S63（S41 常主开 `logits_finite`）。

**Positions÷2 / temp÷50 / RMSNorm-out-negate（S84/S85/S86）：** S84/S85 开 `token_repeat`（S85 需 temperature>0）。S86 **开 `logits_finite`**（主）。S84≠S37/S57；S85≠S36；S86≠S73/S66。

**RMSNorm-out×50 / residual-post-negate / RMSNorm-out÷50（S87/S88/S89）：** S87/S88 **开 `logits_finite`**（主）。S89 开 `token_repeat`。S87≠S62/S86；S88≠S48/S86；S89≠S87/S78。

**Residual-post×50 / residual-post÷50 / temp-skip（S90/S91/S92）：** S90 **开 `logits_finite`**（主）。S91/S92 开 `token_repeat`（S92 需 T>0）。S90≠S55/S64/S88；S91≠S90/S64/S88；S92≠S36/S85。S92 identical precision=0 仍可 PASS。

**Residual←normed-x / residual↔x swap / temp-double（S93/S94/S95）：** S93/S95 开 `token_repeat`（S95 需 T>0）。S94 **开 `logits_finite`**（主）。S93≠S31/S94/S88–S91；S94≠S31/S93/S88；S95≠S36/S85/S92。

**RMSNorm-weight=ones / residual-leak-add / min_p-skip（S96/S97/S98）：** S96/S98 开 `token_repeat`（S98 需 T>0 + min_p）。S97 **开 `logits_finite`**（主）。S96≠S66/S71/S74；S97≠S31/S93/S94/S88–S91；S98≠S36/S85/S92/S95/S46。S96/S98 identical precision=0 仍可 PASS。

**Top_p-skip / RMSNorm-bias=weight / cos/sin-half-swap（S99/S100/S101）：** 开 `token_repeat`（S99 需 T>0 + top_p）。S99≠S45/S98/temp；S100≠S66/S71/S74/S96；S101≠S42/S79–S82/S40/S25/S28。S99 identical precision=0 仍可 PASS。

**RMSNorm-out-abs / SwiGLU-gate-only / rope-skip-key（S102/S103/S104）：** 开 `token_repeat`。S102≠S86/S87–S89；S103≠S39/S50/S56–S81；S104≠S40/S25/S28/S101。S103 identical precision=0 仍可 PASS。

**Rope-skip-query / residual-post-abs / SwiGLU-up-only（S105/S106/S107）：** 开 `token_repeat`。S105≠S104/S40/S25/S28/S101；S106≠S88/S90–S91/S102；S107≠S103/S39/S50。

**Hidden-abs / value-abs / RMSNorm-weight-abs（S108/S109/S110）：** 开 `token_repeat`。S108≠S61/S75；S109≠S58/S51；S110≠S66/S71/S74/S96/S100。S109 identical precision=0 仍可 PASS。

**Key-abs / embed-abs / cos/sin-abs（S111/S112/S113）：** 开 `token_repeat`。S111≠S54/S59/S109；S112≠S69/S43/S80；S113≠S42/S79–S82/S101/S40。S113 identical precision=0 仍可 PASS。

**Query-abs / SwiGLU-out-abs / RMSNorm-x-abs（S114/S115/S116）：** 开 `token_repeat`。S114≠S52/S60/S109/S111；S115≠S67/S72/S103/S107；S116≠S73/S62/S78/S102。

**Query÷50 / key÷50 / residual-pre-abs（S117/S118/S119）：** 开 `token_repeat`。S117≠S60/S52/S114；S118≠S59/S54/S111；S119≠S48/S55/S64/S106。

**RMSNorm-weight=zeros / SwiGLU-input-abs / logits-abs（S120/S121/S122）：** 开 `token_repeat`。S120≠S96/S66/S71/S74/S110；S121≠S56/S76/S81/S115；S122≠S53/S65/S108。S121 identical precision=0 仍可 PASS。

**RMSNorm-bias=-weight / penalty-skip / residual-leak-sub（S123/S124/S125）：** S123/S124 开 `token_repeat`（S124 需 T>0）。S125 **开 `logits_finite`**（主）。S123≠S100/S66/S120；S124≠S46/S98/S99；S125≠S97/S93/S94/S31。S124 identical precision=0 仍可 PASS。

**Hidden-zeros / embed-zeros / cos/sin-zeros（S126/S127/S128）：** 开 `token_repeat`。S126≠S61/S75/S108/S122；S127≠S69/S43/S80/S112；S128≠S42/S79–S82/S101/S113。

**Residual-pre-zeros / query-zeros / SwiGLU-out-zeros（S129/S130/S131）：** 开 `token_repeat`。S129≠S48/S55/S64/S119；S130≠S60/S52/S114/S117；S131≠S67/S72/S115/S103/S107。

**Key-zeros / SwiGLU-input-zeros / cos/sin-ones（S132/S133/S134）：** 开 `token_repeat`。S132≠S54/S59/S111/S118；S133≠S56/S76/S81/S121/S131；S134≠S42/S79–S82/S101/S113/S128。

**Residual-post-zeros / RMSNorm-out-zeros / embed-ones（S135/S136/S137）：** 开 `token_repeat`。S135≠S88/S90/S91/S106/S129；S136≠S86/S87/S89/S102；S137≠S69/S43/S80/S112/S127。

**Hidden-ones / positions-ones / residual-pre-ones（S138/S139/S140）：** 开 `token_repeat`。S138≠S61/S75/S108/S126；S139≠S37/S57/S84；S140≠S48/S55/S64/S119/S129。

**Query-ones / key-ones / SwiGLU-out-ones（S141/S142/S143）：** 开 `token_repeat`。S141≠S60/S52/S114/S117/S130；S142≠S54/S59/S111/S118/S132；S143≠S67/S72/S115/S131。

**Residual-post-ones / RMSNorm-out-ones / SwiGLU-input-ones（S144/S145/S146）：** 开 `token_repeat`。S144≠S88/S90/S91/S106/S135；S145≠S86/S87/S89/S102/S136；S146≠S56/S76/S81/S121/S133。

**Positions-zeros / value-ones / attn-out-ones（S147/S148/S149）：** 开 `token_repeat`。S147≠S139/S57/S84；S148≠S58/S51/S109；S149≠S63/S41/S83。

**RMSNorm-x-ones / logits-ones / RMSNorm-bias-zeros（S150/S151/S152）：** 开 `token_repeat`。S150≠S73/S62/S78/S116；S151≠S122/S53/S65；S152≠S100/S123/S96。
