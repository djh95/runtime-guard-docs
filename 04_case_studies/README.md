# ④ 问题定位实例分析

定位流程以 [02 问题定位](../02_problem_localization/README.md) 为准。

这里放的是**对外保留的 15 个典型案例**：每个案例自己一套材料。

## 案例包标准目录（v2）

每个案例只有外层唯一主文件 `README.md`，证据一律进 `evidence/`：

```text
04_case_studies/
  README.md                         # 本文件：索引 + 名词表 + 包结构
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

keep-set 案例的 **headline 结案**只用下面四档；**不要**再用 PASS / FAIL / GAP 当总评。

| 档 | 含义 |
|----|------|
| **未复现** | 目标异常形态没有出现（有 trigger 也不够；通顺输出 ≠ 目标乱码）。 |
| **复现未抓到** | 异常已现或应现，但**没有有效异常 KV dump** 可做对账（含 `logits_finite`：有 report 却无可用 dump）。mere detect=0 **不是**本档——若 manual dump 已抓到异常 KV 并完成对账，按③/④。**勿**因 logits 命中就跳过 KV、改用 msprobe 顶替本档。 |
| **KV 一致→排除 KV** | 有效异常↔标杆对账，对比窗匹配 → **排除 KV cache** 为本请求坏输出的必要原因。 |
| **KV 不一致→定界** | 有效对账不匹配 → **重开 KV 线**；摘要十问事实（首不一致在 prompt/output、是否恢复、out0 余弦、是否仅 PD…），不从坏输出跳根因。弱窗对账（如 o=1）仍可归本档，但须注明力度有限。 |

**检测**另写：三层数字和/或「检出 / 漏检 / 乱码漏检」等，见名词表。

## 名词怎么读（先看这里）

| 说法 | 含义 |
|------|------|
| **结案（四档）** | 案例**总评主标签**，只取下列四档之一（与「检出与否」分开写）：① **未复现** — 目标异常形态未出现；② **复现未抓到** — 异常已现/应现，但**无有效异常 KV dump** 可对账（若 manual dump 已成功对账，不算本档；也不因 mere detect=0 就归本档）；③ **KV 一致→排除 KV** — 有效对账且匹配；④ **KV 不一致→定界** — 有效对账且不匹配，用十问事实（prompt/output、恢复、out0、PD…）摘要，禁止根因跃迁。 |
| **检测（辅）** | 与结案档并列的辅信息：三层 trigger/precision/detect，和/或短标签「检出 / 漏检 / 乱码漏检 / 无可检（非漏检）」等。**不是**结案总评。 |
| **PASS / FAIL / GAP（历史·检测侧）** | **已退役为结案总评。** 旧文里 PASS≈检出、FAIL≈未过关总称、GAP/FAIL+GAP≈有异常未检出（漏检类）。现只可作 **detector / verify 侧**用语（如 skills 验 detector），**不要**再当案例 headline 结案。无异常时不要写「漏检/GAP」。 |
| **复现失败** | 打了 patch / overlay，但目标异常**没有出现** → 结案档 **未复现**（注明形态/注入/负载等原因）。不要写成漏检。 |
| **样本** | 保存的请求 / 回复证据；应含 prompt + 输出，用来**读文意、核对坏没坏 / 是否误判**。仅有 prompt **字符串**的 sample **不能**当作可靠 tokenize 标杆（发出去的字符串 + 回来的 completion，再 encode 的结果可能与服务端不一致；处理 prompt 与处理 sample 的 tokenizer 也可能不同）。 |
| **标杆请求（token ids）** | 需要可复现 tokenize / 定界对比时，请求侧以服务端或 Guard **实际捕获的 `prompt_token_ids`** 为准，**用 token ids 去抓 / 归档**，禁止「只存字符串、事后再 encode」当标杆。 |
| **KV 排除定界** | 有异常 report 时的可执行路径：重放抓**实际** prompt token ids → 合并异常 **output token ids** → 抓标杆 KV → 对比异常 KV。**一致 → 排除 KV cache**（再转向规格所指的非 KV 类，如 MoE 路由）；**不一致 → 重开 KV 线**。规格里「构造预期：根因是否在 KV」只记构造预期，**不是**跳过该排除步骤。包内未做对比时写「尚未做 KV 对比（未抓标杆/异常 KV 或未写入本包）」；已做则写实数事实。 |
| **三层计数** | **trigger**（注入路径打中次数）/ **precision**（输出被判异常的次数，≠ 模型精度）/ **detect**（Guard 报告命中次数）。三者不相等；见各包 `三层计数.json`。 |
| **三层计数.json** | 三层明细（trigger / precision / detect、备注、detector 名等）。索引表数字通常摘自这里。 |
| **跑批结果.json** | 跑批元数据 + 结案摘要（场景名、verdict、模型、run 路径、三层摘要）。和 `三层计数.json` 一起读。 |
| **Guard pin** | 做异常案例实验时**钉死的 Runtime Guard / 产品树提交**（常见记作 G2 + git SHA，如 `f2aefd068…`，对应 A+#18644 一类合入点）。作用是各案例、各次复现用同一套 Guard 代码，数字可比；`跑批结果.json` 里的 `wt_sha` 即该 pin。不是「别针」或硬件概念。**不是仓库当前最新 commit，而是实验钉死的那一颗**（例 G2=`f2aefd068…`，见跑批 `wt_sha`）。本 keep-set 默认 **MRV2 + 该 pin**。 |
| **复现模式（repro_mode）** | 这一跑**怎么打出异常**：概念上是「基线负载」vs「把**合法 knobs**（并发 / 温度 / util / prompt 形态等）调高以抬复现率」。**仍须**遵守 **origin-faithful**（禁止 NaN / fill 等伪造症状）。**不是**表里的 **Origin** 字段（异常落在哪棵代码树），也**不是** **Guard pin**（钉哪版 Guard）。本仓 `跑批结果.json` / `规格说明.md` 实际出现的枚举只有 **`origin_tuned`**：在 origin-faithful 前提下，用合法 knobs 抬高复现率后的钉点跑法（S23 规格写作 `origin_tuned`（minimal construct），是同值旁注，不是新枚举）。规格表若只列字段无长解释，含义见本 README。 |
| **规格说明.md** | 案例规格：Origin、上游锚点、overlay、knobs、`repro_mode`、期望 detector——**只管复现**；`repro_mode` 白话见上表 **复现模式**。 |
| **overlay / overlay.patch** | 制造异常用的代码补丁；完整补丁在 `evidence/`。 |
| **上游锚点** | 本案例所对照的**上游修复 PR / issue**（「原 bug 是在哪修好的」）。多笔时要标明：根因修复 / 同族相关 / 对照 cousin，不要堆一串无说明链接。 |
| **Origin**（字段） | 案例表格里的 **`Origin`** 标的是**异常逻辑落在哪棵代码树**，取值只有三种：`vllm-only`（只改 / 只坏在上游 vLLM）、`ascend-only`（只改 / 只坏在 Ascend 插件树）、`both`（两边同失败模式，或复现要动双树）。它**不是**「有没有忠实复现」、也不是 PR 好坏分。旁注里的 `constructed` 只说明注入是按该类故障构造的，不改变上述三值。 |
| **origin-faithful** | **复现纪律**：注入要忠于原 bug 逻辑；禁止强制写 NaN、填复读 token 等「伪造症状」。与上表 **Origin 字段**是两件事。文档里**没有**「origin bath」；若看到多半是口误，应指 **origin-faithful** 或 **Origin**。Agent 细则见 [`06_agent_skills/build-anomaly-env`](../06_agent_skills/build-anomaly-env/SKILL.md)。 |
| **force-feed** | 按报告里的 **token id** 原样喂给干净服务（禁止再 tokenize 字符串）。用于抓标杆 KV。 |
| **FE** | **失败证据包**（fail-evidence）：一次复现留下的 samples / reports / 状态摘要等。 |
| **soft-inv / soft-inverse** | 按上游修复做**反向注入**，人为复现同类故障（教学/评测用）。 |
| **CJK** | **中日韩字符**（Chinese / Japanese / Korean）。旧评分曾把「含非 ASCII 的中文」当成 `garbage_mixed_script`，把通顺中文误计成 precision——尤其 S01。现行规则：**排除 CJK 后再计 weird**；通顺中文 ≠ 乱码。 |
| **hybrid / 量化 KV** | 混合或量化的 KV 页语义；和稠密 bf16 不是同一套前提（S01 尤其重要）。 |
| **跨请求内容相同的乱码** | 多次独立请求得到的异常输出彼此相同（同一段垃圾重复出现），不是每次随机不同。常见于 S07。对照：各请求乱码各不相同（如 S45）。 |
| **内容相同计分** | 用「多条回复是否同一段文字」来估 precision 的做法；各请求内容不同时会低估（如 S45 记成 0）。 |
| **复现技巧** | 「怎么跑才能对齐本包结论」的步骤与负载（并发 / prompt / 双树写入等）。**不含** origin-faithful / 禁止 NaN·token fill——那是**构建异常环境 / overlay 构造**纪律，写在 `规格说明.md` 与根因/构造节。旧称「复现配方」已不用；过程旧文称 **历史记录**。 |
## 对外保留的 15 个典型案例

> **2026-10-22 清空实测后重测中：** 基线清空于 `381af71`（仅 overlay+规格）。已回填包见下表实数；其余仍为空。重测按同一次异常请求回填，禁止混用旧跑。

| ID | 包 | 结案 | 检测 | 根因（构造） | 现象 | 检测器（期望） | trigger / precision / detect |
|----|-----|------|------|--------------|------|----------------|------------------------------|
| S01 | [cases/S01/](./cases/S01/) | （空） | （空） | KV 新块未置零（需 hybrid/量化 KV） | （空） | 乱码类 | （空） |
| S10′ | [cases/S10p/](./cases/S10p/) | （空） | （空） | FullAttn 回收块未清零 | （空） | `token_repeat` | （空） |
| S11 | [cases/S11/](./cases/S11/) | （空） | （空） | MLA RoPE pad-tail 错位 | （空） | `token_repeat` | （空） |
| S07 | [cases/S07/](./cases/S07/) | （空） | （空） | W8A8 dequant scale 崩溃 | （空） | `logits_finite` | （空） |
| S23 | [cases/S23/](./cases/S23/) | KV 不一致→定界 | 检出 | 一层 `o_proj` 权重置零 | min_cos≈0.68；prompt idx=1@L35；未用槽有限非0=卫生 | `token_repeat` | 2 / 16 / 48 |
| S45 | [cases/S45/](./cases/S45/) | （空） | （空） | top-k 打在 −logits | （空） | `token_repeat`+`logits_finite` | （空） |
| S43 | [cases/S43/](./cases/S43/) | KV 不一致→定界 | 检出 | embedding ×100 | 换行塌缩 | `token_repeat`×48 | 16 / 40 / 48 |
| S22 | [cases/S22/](./cases/S22/) | （空） | （空） | Spec resample 无独立 salt | （空） | `spec_acceptance` | （空） |
| S06 | [cases/S06/](./cases/S06/) | （空） | （空） | MoE router bias / mask（构造） | （空） | `token_repeat` | （空） |
| S26 | [cases/S26/](./cases/S26/) | **KV 一致→排除 KV** | **检出** | RMSNorm fp32 错乘 | `1.1.1…` 数字复读 | `token_repeat` | **470 / 14 / 48** |
| S25 | [cases/S25/](./cases/S25/) | **KV 一致→排除 KV** | **检出** | RoPE 后半维丢失 | `1.1.1…` 数字复读 | `token_repeat` | **462 / 15 / 48** |
| S50 | [cases/S50/](./cases/S50/) | KV 不一致→定界 | 检出 | SwiGLU gate/up 对调 | 有效槽全 NaN；未用槽亦 NaN；标杆洁；不定层 | `logits_finite` | 58 / 48 / 48 |
| S48 | [cases/S48/](./cases/S48/) | KV 不一致→定界 | 检出 | residual 极性取反 | 全请求 `!!!!…` | `logits_finite`×48 | 44 / 48 / 48 |
| S47 | [cases/S47/](./cases/S47/) | KV 不一致→定界 | 检出 | Attn 前 K/V 对调 | 乱码/复读 | `token_repeat`×48 | 30 / 0（identical×37） / 48 |
| S33 | [cases/S33/](./cases/S33/) | （空） | （空） | softcap 缺 `*cap` rescale | （空） | `token_repeat` | （空） |

计数摘自各包实测回填后的 `evidence/三层计数.json`（已回填者见表；其余为空）。

脚注：S25/S26 钉点 dump 均临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) 以取得非空 `prompt_token_ids`；KV 对比跨度 `p+o-1`（各两组 match）。原始 `.pt` 留服务器 `verified_kv/`（S25≈94M / S26≈75M，未入库）。


`S10′` 在仓库里的目录名是 **`S10p`**。相关 Skills 见 [06](../06_agent_skills/)（**v5.9**）。

## 样本字段

**当前 keep-set 无 `evidence/samples/`（已清空）。** 重测归档后使用：


`evidence/samples/` 里的样本 JSON 使用：

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
