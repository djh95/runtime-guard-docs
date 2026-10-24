# ④ 问题定位实例分析

定位流程以 [02 问题定位](../02_problem_localization/README.md) 为准。

这里放的是**对外保留的 15 个典型案例**（**keep-set**）：每个案例自己一套材料。

**词汇表（用户面入口）：** [词汇表.md](./词汇表.md) — GAP/soft-inv/三层率/origin-faithful/overlay/repro_mode/清洁标杆/force-feed/10-gate/logits 有限乱码 … 一律先查这里。

## 案例包标准目录（v2）

每个案例只有外层唯一主文件 `README.md`，证据一律进 `evidence/`：

```text
04_case_studies/
  README.md                         # 本文件：索引 + 结案四档 + 包结构
  词汇表.md                          # 【用户面】自造词与入口术语
  cases/
    Sxx/                            # S10′ → 目录名 S10p
      README.md                     # 【必选 · 外层唯一主文件】
                                    #   结案四档 + 检测（辅）+ 三层表 + detector 一句
                                    #   1 现象 → 2 根因/构造 → 3 Guard → 4 复现技巧
                                    #   → 5 定界（事实→推论→结论）→ 6 证据 → 7 上游 PR
                                    #   （origin-faithful / 勿 NaN·fill 写在规格·构造，不写进复现技巧）
      evidence/
        overlay.patch               # 【必选】静态补丁
        规格说明.md                  # 【必选】只管复现：Origin / 锚点 / overlay / knobs / 期望 detector
        三层计数.json                # 推荐：trigger / precision / detect 明细
        跑批结果.json                # 推荐：跑批元数据 + 结案摘要
        samples/                    # 条件：宣称 precision>0 → ≥1 份 prompt+completion
        reports/                    # 实测后按需；当前 keep-set 为空
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

keep-set 案例的 **headline 结案**只用下面四档；检测辅标只用「检出 / 漏检 / 乱码漏检」等——**不要**再用 PASS / FAIL / GAP / FAIL+GAP / PASS·FAIL 当总评或标题。

| 档 | 含义 |
|----|------|
| **未复现** | 目标异常形态没有出现（有 trigger 也不够；通顺输出 ≠ 目标乱码）。 |
| **复现未抓到** | 异常已现或应现，但**没有有效异常 KV dump** 可做对账（含 `logits_finite`：有 report 却无可用 dump）。mere detect=0 **不是**本档——若 manual dump 已抓到异常 KV 并完成对账，按③/④。**勿**因 logits 命中就跳过 KV、改用 msprobe 顶替本档。 |
| **KV 一致→排除 KV** | 有效异常↔标杆对账，对比窗匹配 → **排除 KV cache** 为本请求坏输出的必要原因。 |
| **KV 不一致→定界** | 有效对账不匹配 → **重开 KV 线**；摘要十问事实（首不一致在 prompt/output、是否恢复、out0 余弦、是否仅 PD…），不从坏输出跳根因。弱窗对账（如 o=1）仍可归本档，但须注明力度有限。 |

**检测**另写：三层数字和/或「检出 / 漏检 / 乱码漏检」等，见 [词汇表](./词汇表.md)。

## 名词怎么读

**完整释义 → [词汇表.md](./词汇表.md)**（含 GAP 退役说明、soft-inv、清洁标杆、force-feed、三层率、origin-faithful、repro_mode 四态、amplifier、A/B/C、10-gate、logits 有限乱码等）。

本页只留 keep-set 阅读时最常用的几条；其余勿只在 PRINCIPLES / skills 里找。

| 说法 | 含义（摘要） |
|------|------|
| **结案（四档）** | 总评主标签：未复现 / 复现未抓到 / KV 一致→排除 KV / KV 不一致→定界（详上节）。 |
| **检测（辅）** | 三层 trigger/precision/detect，和/或「检出 / 漏检 / 乱码漏检」——**不是**结案总评。 |
| **（勿用）旧 PASS / FAIL / GAP** | **退役结案标签**；现用四档 + 漏检类检测辅标。见 [词汇表 · GAP](./词汇表.md)。 |
| **三层率** | trigger ≠ precision ≠ detect。见 [词汇表](./词汇表.md)。 |
| **overlay** | 案例里的 `overlay.patch`＝故障补丁；启服里的 `runtime_config` overlay＝配置合并（两义，见词汇表）。 |
| **origin-faithful / repro_mode** | 复现纪律 vs 四态字段；见 [词汇表](./词汇表.md)。 |
| **清洁标杆 / force-feed** | 未注入对照 + 按 token id 原样喂；见 [词汇表](./词汇表.md)。 |
| **样本 vs 标杆请求** | sample 字符串只读文意；tokenize标杆用实际 `prompt_token_ids`。 |
| **复现技巧** | 「怎么跑才对齐本包结论」；构造纪律（勿 NaN/fill）写在规格/根因，不进复现技巧。 |

## 对外保留的 15 个典型案例

> **2026-10-23：** keep-set **15 包均已回填**（基线曾清空于 `381af71`）。下表数字摘自各包 `evidence/三层计数.json`；结案为四档用语。禁止混用旧跑。

| ID | 包 | 结案 | 检测 | 根因（构造） | 现象 | 检测器（名字） | 触发 / 判坏 / 报告数 |
|----|-----|------|------|--------------|------|--------|------------------------------|
| S01 | [cases/S01/](./cases/S01/) | KV 一致→排除 KV（dense） | 检出 | 新 KV block 未置零 | 部分数字复读（非目标 hybrid/量化形态） | `token_repeat` | 82 / 16 / 48 |
| S06 | [cases/S06/](./cases/S06/) | KV 不一致→定界 | 检出 | MoE 路由 bias | token 重复 | `token_repeat` | 52 / 25 / 46 |
| S07 | [cases/S07/](./cases/S07/) | KV 不一致→定界（有效槽全零） | 乱码漏检 | W8A8 scale 崩溃 | 跨请求内容相同的乱码×48 | 期望抓非有限 logits→0 报告；手动抓 KV | 74 / 48 / 0 |
| S10p | [cases/S10p/](./cases/S10p/) | KV 一致→排除 KV | 检出 | FullAttn 回收块未清零 | token 重复 / 垃圾 | `token_repeat` | 64 / 17 / 64 |
| S11 | [cases/S11/](./cases/S11/) | KV 不一致→定界 | 检出 | MLA RoPE pad | token 重复 | `token_repeat` | 108 / 27 / 48 |
| S22 | [cases/S22/](./cases/S22/) | KV 不一致→定界（一对分 / 一对 clean） | 检出 | Spec resample 无独立 salt | 投机接受率异常（无乱码文本） | `spec_acceptance` | 116 / 0 / 48 |
| S23 | [cases/S23/](./cases/S23/) | KV 不一致→定界 | 检出 | 一层 `o_proj` 权重置零 | 部分数字复读 | `token_repeat` | 2 / 16 / 48 |
| S25 | [cases/S25/](./cases/S25/) | KV 一致→排除 KV | 检出 | RoPE 后半维丢失 | `1.1.1…` 数字复读 | `token_repeat` | 462 / 15 / 48 |
| S26 | [cases/S26/](./cases/S26/) | KV 一致→排除 KV | 检出 | RMSNorm fp32 错乘 | `1.1.1…` 数字复读 | `token_repeat` | 470 / 14 / 48 |
| S33 | [cases/S33/](./cases/S33/) | KV 一致→排除 KV | 检出 | softcap 缺 `*cap` rescale | 数字 / token 复读 | `token_repeat` | 102 / 15 / 48 |
| S43 | [cases/S43/](./cases/S43/) | KV 不一致→定界 | 检出 | embedding ×100 | 输出几乎只剩换行/空白 | `token_repeat` | 16 / 40 / 48 |
| S45 | [cases/S45/](./cases/S45/) | KV 一致→排除 KV（只对上 prompt 短窗） | 乱码漏检 | top-k 打在 −logits | 乱码/空 completion（相同串×16） | 两种检测都 0 报告；手动抓 KV | 16 / 16 / 0 |
| S47 | [cases/S47/](./cases/S47/) | KV 不一致→定界 | 检出 | Attn 前 K/V 对调 | 乱码/复读（37 条内容相同；自动判坏计数=0） | `token_repeat` | 30 / 0 / 48 |
| S48 | [cases/S48/](./cases/S48/) | KV 不一致→定界 | 检出 | residual 极性取反 | 全请求 `!!!!…` | `logits_finite` | 44 / 48 / 48 |
| S50 | [cases/S50/](./cases/S50/) | KV 不一致→定界 | 检出 | SwiGLU gate/up 对调 | 有效槽 NaN；首分歧约第 3–6 层 | `logits_finite` | 58 / 48 / 48 |

脚注：S25/S26 钉点 dump 均临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) 以取得非空 `prompt_token_ids`；KV 对比跨度 `p+o-1`（各两组 match）。原始 `.pt` 留服务器 `verified_kv/`（未入库）。

`S10′` 目录名是 **`S10p`**。相关 Skills 见 [06](../06_agent_skills/)（**v5.17**，见 `SKILLS_METADATA.md`）。

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

案例 README「### 事实」与 agent **【事实总结】**须用**展开白话**（skills **v5.20**；风格同已归档 keep-set）：术语**首次出现先解释**（清洁标杆、`o=1`、两对同向、有效槽、格、数值门闩、dump 双名等），写清「发生了什么→检出没→KV 结论」；禁止只堆 `first_cos` / `tok0@L*` 半截句。数字与 tip 不编造。细则见 [`investigation` · 事实写作](../06_agent_skills/investigation/SKILL.md)。

### KV 对账表（案例写作约定）

对账顺序（与 skills **v5.20.2** 一致）：先 shape/掩未用槽 → **有效槽数值问题先写入事实（带子类型、白话）** → 再余弦与下表。必现但 detect=0 时可用 `manual_dump` 抓 KV。有 **buggy KV + 清洁标杆 KV** 且已写入 `evidence/kv_compare.json` / `kv_v516_numeric_first.json` 时，在 README「### 事实」**之后**、「### 推断」**之前**补两张表（白话；数字只来自证据）：

1. **表1 · 每 token 最差格** — 行=对比窗内每个 token（标 prompt/out 角色与序号）；格内取该 token **差距最大的层**（最差余弦）。若该 token 触发 v5.16 **数值问题** → 写清子类型（如 **`数值问题:全零(zero_norm)` / `数值问题:NaN` / `数值问题:Inf`**），**不要**只写「数值异常」、**不要**再填余弦。
2. **表2 · 首个出问题的 token 的逐层剖面（合并区间）** — **不是**「对比窗第一个 token / window token0」的固定图。  
   - **目标 token** = 窗内**第一个已出现 KV 问题**的 token：有效槽 **数值问题**，或该 token 最差余弦已明显不对（低于阈值，如 &lt;0.99）。文中写清角色（如 `prompt[1]` / `out[6]`）。  
   - 若 **prompt[0] 即首坏**：表2 画它的逐层合并区间，并标明「首个出问题的 token = prompt[0]」。  
   - 若 **首 token 干净、更晚才坏**：表2 **必须**画那个首坏 token；画干净的 prompt[0] **没用**。包内若只有该 token 的锚点（`first_cos_mismatch` 的 `min_layer`/`min_cos` 等）而无完整逐层数组 → **只写锚点 + 注明无逐层数组**，禁止用 `clean_model_tok0_cos` 冒充。  
   - 若 **全程≈1（排除 KV）/ 无问题 token**：表2 写「无问题 token，跳过」或一行说明对比窗全程≈1——**不要**假装「首坏」。

分桶（可读性）：`≈1`≥0.99；`0.9–0.99`；`0.8–0.9`；`0.6–0.8`；`0.3–0.6`；`0.1–0.3`；`<0.1`（含负值）；数值门闩写 **子类型**（不编余弦）。

多对同向只展示代表对；对与对结论不一致（如 S22）则分列或标明。无逐 token / 逐层数组时**简短说明并跳过**，禁止用摘要脑补整表。

