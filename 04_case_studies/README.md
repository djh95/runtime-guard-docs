# ④ 问题定位实例分析

定位流程以 [02 问题定位](../02_problem_localization/README.md) 为准。

这里放的是**对外 keep-set**（精简后按**分析结论类型各留一例**；深度标杆 A/B 另造补齐）：每个案例自己一套材料。已移出包见 [`_retired/`](./_retired/)。

少数稳定缩写见 [短词汇表](./词汇表.md)（keep-set / overlay / 三层率 / 清洁标杆 / Guard pin / force-feed）。其余在正文用白话写清即可。

## 案例包标准目录（v2）

每个案例只有外层唯一主文件 `README.md`，证据一律进 `evidence/`：

```text
04_case_studies/
  README.md                         # 本文件：索引 + 结案四档 + 包结构
  词汇表.md                          # 短表：仅稳定缩写
  cases/
    Sxx/                            # S10′ → 目录名 S10p
      README.md                     # 【必选 · 外层唯一主文件】
                                    #   结案四档 + 检测（辅）+ 三层表 + detector 一句
                                    #   1 现象 → 2 根因/构造 → 3 Guard → 4 复现技巧
                                    #   → 5 定界（事实→推论→结论）→ 6 证据 → 7 上游 PR
                                    #   （构造须忠于原 bug；勿强写 NaN/填假 token——写在规格·构造，不写进复现技巧）
      evidence/
        overlay.patch               # 【必选】故障补丁
        规格说明.md                  # 【必选】只管复现：落在哪棵树 / 上游锚点 / 补丁 / 负载旋钮 / 期望 detector
        三层计数.json                # 推荐：触发 / 判坏 / 报告 明细
        跑批结果.json                # 推荐：跑批元数据 + 结案摘要
        samples/                    # 条件：宣称有异常输出 → ≥1 份 prompt+completion
        reports/                    # 有检出时归档 report；现行 keep-set 各包均有
```

### 各文件作用

| 路径 | 作用 |
|------|------|
| `cases/Sxx/README.md` | **人读主入口**：结案 + 三层 + detector + **定界分析**（事实→推论→结论）+ 现象/案例背景·构造/复现技巧/证据表/上游 PR |
| `evidence/overlay.patch` | 制造异常的代码补丁（包内必有） |
| `evidence/规格说明.md` | **只写怎么复现**（Origin、锚点、overlay、knobs、期望 detector）；不定界长文 |
| `evidence/三层计数.json` | 机读三层数字；人读以 README 表为准 |
| `evidence/跑批结果.json` | 机读跑批/结案元数据；人读以 README 为准 |
| `evidence/samples/` | 坏/对照输出原文（prompt + completion）——**阅读 / 现象核对**；非 tokenize 标杆 |
| `evidence/reports/` | Guard detector 真实报告；其中非空的 `prompt_token_ids` 才是请求侧 tokenize **标杆** |

**人读优先级：** `README.md` ≫ `规格说明.md` · `overlay.patch`。

**一个案例只留最终钉点**一套数字 / 样本 / report。

**只钉一轮（硬）：** 对外包内三层 / samples / reports / KV compare / 表1·表2 / 结案·事实必须来自**同一 verified 跑批波次**。禁止混用更早残留目录或其他 `req_id` 的数改结案或补表；重跑则**整包替换** evidence 并重写事实/结案。多组同波：结论一致对外只留一组；不一致如实写（如一对分/一对干净），禁止揉成假同向。Skills **v5.20.10**。

**对外脱敏：** keep-set 归档（含 `跑批结果.json` / 规格实测尾）**禁止**写入内网 IP / 实验室主机名；机器角色用 `builder 机` / `skills 机`（与既有 hygiene 一致）。

定界写作纪律、KV 时机推演、案例禁写句 → [investigation skill](../06_agent_skills/investigation/SKILL.md)。细问序走 [02 §5 十问](../02_problem_localization/README.md#5-kv-定界十问检查单有-buggyref-时按序)；PD 单边对照见同页 Step 0.5。

### 必选 / 条件

| 项 | 级别 |
|----|------|
| `README.md`（结案 + 定界） | 必选 |
| `evidence/overlay.patch` | 必选 |
| `evidence/规格说明.md` | 必选（只管复现） |
| `三层计数.json` · `跑批结果.json` | 强烈建议 |
| `samples/` | 条件必选（有 precision 宣称） |
| `reports/` | 条件必选（detect>0，有检出） |

## 结案四档（主标签）

案例的 **headline 结案**只用下面四档；检测辅标只用「检出 / 漏检 / 乱码漏检」等——不要再用旧的 PASS / FAIL /「漏检总评」当标题。

| 档 | 含义 |
|----|------|
| **未复现** | 目标异常形态没有出现（注入路径打中也不够；通顺输出 ≠ 目标乱码）。 |
| **复现未抓到** | 异常已现或应现，但**没有有效异常 KV dump** 可做对账（含 `logits_finite`：有 report 却无可用 dump）。仅「报告数为 0」**不是**本档——若已手动抓到异常 KV 并完成对账，按③/④。**勿**因 logits 命中就跳过 KV、改用 msprobe 顶替本档。 |
| **KV 一致→排除 KV** | 异常侧与清洁标杆对账，对比窗匹配 → **排除 KV cache** 为本请求坏输出的必要原因。 |
| **KV 不一致→定界** | 有效对账不匹配 → **重开 KV 线**；摘要十问事实（首不一致在 prompt/output、是否恢复、输出第一个 token 的余弦、是否仅 PD…），不从坏输出跳根因。弱窗对账（如生成只吐了 1 个 token）仍可归本档，但须注明力度有限。**深度金标**（跨 token 坏→恢复、层计算平台、仅 PD）见 [investigation · 时机方法示例](../06_agent_skills/investigation/SKILL.md)；现行 15 包多为 tok0 起全脏 / 数值问题 / 排除 KV，未齐备该形态。 |

**检测**另写：三层数字（触发 / 判坏 / 报告）和/或「检出 / 漏检 / 乱码漏检」。乱码漏检常见于：**logits 仍有限**（无 NaN/Inf）但语义已是乱码——`logits_finite` 抓不到。

## 阅读时几句白话

| 说法 | 白话 |
|------|------|
| **结案 / 检测** | 结案用上面四档；检出与否另写，不要混成一个总评。 |
| **三层数字** | 触发（注入打中）≠ 判坏（输出已异常）≠ 报告（Guard 命中）；见 [短词汇表](./词汇表.md)。 |
| **故障补丁 vs 启动配置** | 案例 `overlay.patch`＝制造异常；启服里的 `runtime_config`＝配置覆盖，不是打故障（见词汇表 **overlay**）。 |
| **构造纪律** | 补丁要走与原 bug **同一逻辑**；禁止强写 NaN、填假复读 token 来「假装复现」。规格「复现方式」写这跑怎么抬复现率（本集多为合法旋钮调高后的钉点），不是结案标签。 |
| **清洁标杆 / 原样喂 token** | 对照用未打故障的服务；抓对照 KV 时按报告 **token id 原样喂**，不要把字符串再 tokenize（见词汇表）。 |
| **样本 vs 标杆请求** | sample 字符串只读文意；要对齐 tokenize 须用服务端实际抓到的 `prompt_token_ids`。 |
| **复现技巧** | 「怎么跑才对齐本包结论」；构造纪律写在规格/根因，不进复现技巧。 |
| **Guard pin** | 钉死的 Guard 提交（常见 G2 + `f2aefd068…`），保证案例间数字可比。 |

## 对外 keep-set（一类一例 · 2026-10-24）

> 按**分析结论类型**各留一例；数字摘自各包 `evidence/三层计数.json`。禁止混用旧跑 / 其他波次。已移出见 [`_retired/`](./_retired/)。深度金标：**A 完整（S60）+ B（S61）均已进 keep-set**。

| ID | 类型代表 | 包 | 结案 | 检测 | 根因（构造） | 现象 | 检测器 | 触发 / 判坏 / 报告 |
|----|----------|-----|------|------|--------------|------|--------|-------------------|
| S06 | tok0 全脏无恢复 | [cases/S06/](./cases/S06/) | KV 不一致→定界 | 检出 | MoE 路由 bias | token 重复 | `token_repeat` | 52 / 25 / 46 |
| S07 | 漏检 + manual_dump + 全零 | [cases/S07/](./cases/S07/) | KV 不一致→定界（有效槽全零） | 乱码漏检 | W8A8 scale 崩溃 | 跨请求相同乱码×48 | 期望非有限 logits→0；手动抓 KV | 74 / 48 / 0 |
| S11 | 首坏略晚（prompt[1]） | [cases/S11/](./cases/S11/) | KV 不一致→定界 | 检出 | MLA RoPE pad | token 重复 | `token_repeat` | 108 / 27 / 48 |
| S22 | 晚 out / 一对分 | [cases/S22/](./cases/S22/) | KV 不一致→定界（一对分叉 / 一对干净） | 检出 | Spec resample 无独立 salt | 投机接受率异常 | `spec_acceptance` | 116 / 0 / 48 |
| S25 | 排除 KV | [cases/S25/](./cases/S25/) | KV 一致→排除 KV | 检出 | RoPE 后半维丢失 | `1.1.1…` 数字复读 | `token_repeat` | 462 / 15 / 48 |
| S48 | logits_finite / 全 NaN | [cases/S48/](./cases/S48/) | KV 不一致→定界（有限性；不定层） | 检出 | residual 极性取反 | 全请求 `!!!!…` | `logits_finite` | 44 / 48 / 48 |
| S60 | 金标 A · 完整（PD 类） | [cases/S60/](./cases/S60/) | KV 不一致→定界 | 检出 | 中段槽 + out0 target-cos | 坏→恢复 + out0 早层≈0.8 | `token_repeat` | 6056 / 29 / 48 |
| S61 | 金标 B · 层平台 | [cases/S61/](./cases/S61/) | KV 不一致→定界 | 检出 | 晚 decode 层门控 target-cos | tok20 起 L12 跌→0.8–0.9 平台 | `token_repeat` | 86 / 21 / 48 |

脚注：S25 钉点 dump 曾临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) 以取得非空 `prompt_token_ids`；KV 对比跨度 prompt 长度 + 输出长度 − 1。原始 `.pt` 应留服务器耐久 `verified_kv/`（未入库；须落 home，勿只放容器路径）。

相关 Skills 见 [06](../06_agent_skills/)（**v5.20.11**，见 `SKILLS_METADATA.md`）。

## 样本字段

各包归档后在 `evidence/samples/`。样本 JSON 使用：

```json
{
  "prompt": "请求原文",
  "completion": "模型输出文本",
  "api_response": { }
}
```

`api_response` 是原始 `/v1/completions` 响应（可选但建议保留）。只看 `completion` 不够——对照时要连 prompt 一起看。

### 证据说明（摘）

- **阅读 vs 标杆（分层）**
  - **阅读**：完整 prompt / completion 文本看 `evidence/samples/`（文意、坏输出形态、误判核对）。
  - **标杆（tokenize / 定界对比）**：以 report（或其它 Guard/服务端路径）里**实际捕获的 `prompt_token_ids`** 为准；不要用 sample 字符串再 encode。

### 事实写作（白话扩写）

案例 README「### 事实」与 agent **【事实总结】**须用**展开白话**（skills **v5.20**；风格同已归档 keep-set）：术语**首次出现先解释**（清洁标杆、输出只有 1 个 token、两对同向、有效槽、格、数值问题、dump 双名等），写清「发生了什么→检出没→KV 结论」；禁止只堆 `first_cos` / `tok0@L*` 半截句。数字与 tip 不编造。细则见 [`investigation` · 事实写作](../06_agent_skills/investigation/SKILL.md)。

### KV 对账表（案例写作约定）

对账顺序（与 skills **v5.20.10** 一致）：先 shape/掩未用槽 → **有效槽与未用槽分写**（有效：数值问题子类型优先；未用：0 / 有限非零 / NaN·Inf——**勿写「未用一定填 0」**）→ 再余弦与下表。必现但 detect=0 时可用 `manual_dump` 抓 KV。有 **buggy KV + 清洁标杆 KV** 且已写入 `evidence/kv_compare.json` / `kv_v516_numeric_first.json` 时，在 README「### 事实」**之后**、「### 推断」**之前**补两张表（白话；数字只来自证据）：

1. **表1 · 每 token 最差格** — 行=对比窗内 token（标 prompt/out 角色与序号）；格内取该 token **差距最大的层**（最差余弦）或数值问题子类型。格式统一：`token 序号 | 角色 | bucket/min_cos 或 数值问题:…（注）`。若该 token 触发 v5.16 **数值问题** → 写清子类型（如 **`数值问题:全零(zero_norm)` / `数值问题:NaN` / `数值问题:Inf`**），**不要**只写「数值异常」、**不要**再填余弦。**有首坏时必须展示其后若干 out**（可合并区间或抽样）；仅当对比窗本身无后续 out（如 history 止于 prompt）才注明「本包对比窗无后续 out」。禁止「见表面 2」类笔误——写 **表2**。
2. **表2 · 首个出问题的 token 的逐层剖面** — **不是**「对比窗第一个 token / window token0」的固定图。  
   - **目标 token** = 窗内**第一个已出现 KV 问题**的 token：有效槽 **数值问题**，或该 token 最差余弦已明显不对（低于阈值，如 &lt;0.99）。文中写清角色（如 `prompt[1]` / `out[6]`）。  
   - 若 **prompt[0] 即首坏**：表2 画它的逐层剖面，并标明「首个出问题的 token = prompt[0]」。  
   - 若 **首 token 干净、更晚才坏**：表2 **必须**画那个首坏 token；画干净的 prompt[0] **没用**。  
   - **合并区间 = 可读性可选**（连续同分桶可合并）。**合并不了或未合并 → 画全层逐行余弦**；**禁止**因「不好合并」改成只写 `first_mismatch` 锚点摘要。无数组时须先从 buggy+ref `.pt` 跑出 `kv_v516_numeric_first.json`；仅当服务器张量已不存在才允许锚点 + 注明缺数组。禁止用 `clean_model_tok0_cos` 冒充。  
   - 若 **全程≈1（排除 KV）/ 无问题 token**：表2 写「无问题 token，跳过」或一行说明对比窗全程≈1——**不要**假装「首坏」。

分桶（可读性）：`≈1`≥0.99；`0.9–0.99`；`0.8–0.9`；`0.6–0.8`；`0.3–0.6`；`0.1–0.3`；`<0.1`（含负值）；数值问题写 **子类型**（不编余弦）。

多对同向只展示代表对；对与对结论不一致（如 S22）则分列或标明。禁止用窗摘要脑补整表。

