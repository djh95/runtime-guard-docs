# ④ 问题定位实例分析

定位流程以 [02 问题定位](../02_problem_localization/README.md) 为准。

这里放的是**对外保留的 15 个典型案例**：每个案例自己一套材料。

## 案例包标准目录（v2）

每个案例只有外层唯一主文件 `README.md`，证据一律进 `evidence/`：

```text
04_case_studies/
  README.md                         # 本文件：索引 + 名词表 + 标准说明
  cases/
    Sxx/                            # S10′ → 目录名 S10p
      README.md                     # 【必选 · 外层唯一主文件】
                                    #   结案标签 + 三层表 + detector 一句
                                    #   + 现象 / 案例背景·构造 / Guard + 复现技巧 + 教学要点
                                    #   + 定界分析（事实 → 推断 → 结论；末行 L1/L2 标签）
                                    #   + 证据文件表 + 上游 PR 关系 + Origin
      evidence/
        overlay.patch               # 【必选】静态补丁
        规格说明.md                  # 【必选】只管复现：Origin / 锚点 / overlay / knobs / 期望 detector
        三层计数.json                # 推荐：trigger / precision / detect 明细
        跑批结果.json                # 推荐：跑批元数据 + 结案摘要
        samples/                    # 条件：宣称 precision>0 → ≥1 份 prompt+completion
        reports/                    # 条件：PASS 且 detect>0 → ≥1 份真实 report
```

### 各文件作用

| 路径 | 作用 |
|------|------|
| `cases/Sxx/README.md` | **人读主入口**：结案 + 三层 + detector + **定界分析**（事实→推断→结论；末行 L1/L2）+ 现象/案例背景·构造/复现技巧/证据表/上游 PR |
| `evidence/overlay.patch` | 制造异常的代码补丁（包内必有） |
| `evidence/规格说明.md` | **只写怎么复现**（Origin、锚点、overlay、knobs、期望 detector）；不定界长文 |
| `evidence/三层计数.json` | 机读三层数字；人读以 README 表为准 |
| `evidence/跑批结果.json` | 机读跑批/结案元数据；人读以 README 为准 |
| `evidence/samples/` | 坏/对照输出原文（prompt + completion）——**阅读 / 现象核对**；非 tokenize 标杆 |
| `evidence/reports/` | Guard detector 真实报告；其中非空的 `prompt_token_ids` 才是请求侧 tokenize **标杆** |

**人读优先级：** `README.md` ≫ `规格说明.md` · `overlay.patch`。

**一个案例只留最终钉点**一套数字 / 样本 / report。

### 必选 / 条件

| 项 | 级别 |
|----|------|
| `README.md`（结案 + 定界） | 必选 |
| `evidence/overlay.patch` | 必选 |
| `evidence/规格说明.md` | 必选（只管复现） |
| `三层计数.json` · `跑批结果.json` | 强烈建议 |
| `samples/` | 条件必选（有 precision 宣称） |
| `reports/` | 条件必选（PASS 且 detect>0） |

## 定界写作标准（keep-set）

定界节必须有**推理逻辑**，顺序固定：

1. **事实** — 只列包内可核对项：现象文本、三层计数、report / detector、`prompt_token_ids` 是否空、是否已做同 prompt re-curl、KV 对比是否已归档（未归档就写「路径可用；归档尚未附结论」）。少括号旁注，短 bullet；不编造未跑的 KV 数字。
2. **推论**（可写作「推断」）— 只写事实支撑得住的允许/排除；不够就写推不出什么。
3. **结论** — 写清**已定界到** / **尚未定界到**；定界不出写「分析不出 / 尚未定界到… / 证据不足」。**禁止**把 overlay / 上游 PR 已知根因写成定界已证。

**L1/L2：** 优先不写。若保留，仅作文末一行「定界停在哪」**可选**标签——**禁止**当分析骨架或首条 bullet。

**禁止**

- **现象直接等于根因**（反例 S06：坏输出 →「所以进错专家 / MoE topk」）。
- 把「案例背景/构造」（已知 overlay / PR 意图）塞进定界的推论或结论里冒充推出。

构造已知根因放在 README 的「案例背景/构造」（或原「根因」节），与定界分开。

## 名词怎么读（先看这里）

| 说法 | 含义 |
|------|------|
| **PASS** | 异常按预期出现，且期望的 detector **命中**（有 report）。 |
| **FAIL** | 未达到 PASS 的总称（复现没出来，或复现出来了但没检出，都算 FAIL）。 |
| **GAP** | **检测能力缺口**这种问题类型（例如只抓 NaN、抓不住有限乱码）。是缺口分类，不是单独一种「跑失败」标签。 |
| **FAIL+GAP** | 结论标签：异常（或目标坏输出）**已经出现**，但 detector **没检出**——既记未过关（FAIL），又标成检测缺口（GAP）。**有异常是前提**；没有异常出现时不要写 FAIL+GAP。 |
| **复现失败** | 打了 patch / overlay，但目标异常**没有出现**。不要写 GAP。结论记 **FAIL**，并注明原因（形态不对、注入未打中、负载不够、patch 未真正生效等）。可简称 **FAIL（复现未出现）** / **repro-blocked**。 |
| **结案结论** | 写在案例上的判定标签（PASS / FAIL+GAP / FAIL（复现未出现）等），标明是否按预期复现并检出。 |
| **样本** | 保存的请求 / 回复证据；应含 prompt + 输出，用来**读文意、核对坏没坏 / 是否误判**。仅有 prompt **字符串**的 sample **不能**当作可靠 tokenize 标杆（发出去的字符串 + 回来的 completion，再 encode 的结果可能与服务端不一致；处理 prompt 与处理 sample 的 tokenizer 也可能不同）。 |
| **标杆请求（token ids）** | 需要可复现 tokenize / 定界对比时，请求侧以服务端或 Guard **实际捕获的 `prompt_token_ids`** 为准，**用 token ids 去抓 / 归档**，禁止「只存字符串、事后再 encode」当标杆。report 里 prompt 已空时：把**同一 prompt 再 curl**，手动 dump 取服务端实际 ids（仍禁止离线再 tokenize）。 |
| **report 空 prompt** | report 里 `prompt_token_ids` / `prompt_text` 可能为空（output 仍常有）。**常见根因（热重载路径，S06 时序实测）**：首包 `scheduled_new_reqs` prefill 波上 `needs_sample_phase_hooks()` 仍为 false，Bug #9 预缓存整段被跳过，Store **从未写入** prompt；snapshot 时未必已 finished / clear。**不要**写成「请求结束后 clear / reap 过早导致本条空 prompt」——`clear`→zombie 是代码上的另一充分路径，但**不是** S06 空 report 的实测路径。**不是**请求没带 prompt，也不是脱敏。合入 [vllm-ascend#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) 后预缓存不再绑 hooks，同路径应写出非空 ids；本仓 keep-set **旧归档**可能仍为空（合修前样本）。空 ids **不等于**没有 `block_ids` / 不能武装 `dump_kv`，也**不等于**「Q1–Q5 不适用」——有 report 即可：**同 prompt 再 curl** 抓服务端 ids，与异常 `output_token_ids` 合并后做 **KV 排除定界**。**阅读**原文 → samples；**不要**从字符串补造 ids 填进旧 report。 |
| **KV 排除定界** | 有异常 report 时的可执行路径：重放抓**实际** prompt token ids → 合并异常 **output token ids** → 抓标杆 KV → 对比异常 KV。**一致 → 排除 KV cache**（再转向规格所指的非 KV 类，如 MoE 路由）；**不一致 → 重开 KV 线**。规格字段 **`KV?=否`** 只表示根因**预期**不在 KV，**不是**跳过该排除步骤。包内若尚未附对账结果，应写明「路径可用；本案例归档尚未附 KV 对比结论」，**不要**写「Q1–Q5 不适用」，也**不要**编造未跑的对比数字。 |
| **三层计数** | **trigger**（注入路径打中次数）/ **precision**（输出被判异常的次数，≠ 模型精度）/ **detect**（Guard 报告命中次数）。三者不相等；见各包 `三层计数.json`。 |
| **三层计数.json** | 三层明细（trigger / precision / detect、备注、detector 名等）。索引表数字通常摘自这里。 |
| **跑批结果.json** | 跑批元数据 + 结案摘要（场景名、verdict、模型、run 路径、三层摘要）。和 `三层计数.json` 一起读。 |
| **Guard pin** | 做异常案例实验时**钉死的 Runtime Guard / 产品树提交**（常见记作 G2 + git SHA，如 `f2aefd068…`，对应 A+#18644 一类合入点）。作用是各案例、各次复现用同一套 Guard 代码，数字可比；`跑批结果.json` 里的 `wt_sha` 即该 pin。不是「别针」或硬件概念。**不是仓库当前最新 commit，而是实验钉死的那一颗**（例 G2=`f2aefd068…`，见跑批 `wt_sha`）。本 keep-set 默认 **MRV2 + 该 pin**。 |
| **复现模式（repro_mode）** | 这一跑**怎么打出异常**：概念上是「基线负载」vs「把**合法 knobs**（并发 / 温度 / util / prompt 形态等）调高以抬复现率」。**仍须**遵守 **origin-faithful**（禁止 NaN / fill 等伪造症状）。**不是**表里的 **Origin** 字段（异常落在哪棵代码树），也**不是** **Guard pin**（钉哪版 Guard）。本仓 `跑批结果.json` / `规格说明.md` 实际出现的枚举只有 **`origin_tuned`**：在 origin-faithful 前提下，用合法 knobs 抬高复现率后的钉点跑法（S23 规格写作 `origin_tuned`（minimal construct），是同值旁注，不是新枚举）。规格表若只列字段无长解释，含义见本 README。 |
| **规格说明.md** | 案例规格：Origin、上游锚点、overlay、knobs、`repro_mode`、期望 detector——**只管复现**；`repro_mode` 白话见上表 **复现模式**。 |
| **overlay / overlay.patch** | 制造异常用的代码补丁；完整补丁在 `evidence/`。 |
| **上游锚点** | 本案例所对照的**上游修复 PR / issue**（「原 bug 是在哪修好的」）。多笔时要标明：根因修复 / 同族相关 / 对照 cousin，不要堆一串无说明链接。 |
| **Origin**（字段） | 案例表格里的 **`Origin`** 标的是**异常逻辑落在哪棵代码树**，取值只有三种：`vllm-only`（只改 / 只坏在上游 vLLM）、`ascend-only`（只改 / 只坏在 Ascend 插件树）、`both`（两边同失败模式，或复现要动双树）。它**不是**「有没有忠实复现」、也不是 PR 好坏分。旁注里的 `constructed` 只说明注入是按该类故障构造的，不改变上述三值。 |
| **origin-faithful** | **复现纪律**：注入要忠于原 bug 逻辑；禁止强制写 NaN、填复读 token 等「伪造症状」。与上表 **Origin 字段**是两件事。文档里**没有**「origin bath」；若看到多半是口误，应指 **origin-faithful** 或 **Origin**。 |
| **CJK** | **中日韩字符**（Chinese / Japanese / Korean）。旧评分曾把「含非 ASCII 的中文」当成 `garbage_mixed_script`，把通顺中文误计成 precision——尤其 S01。现行规则：**排除 CJK 后再计 weird**；通顺中文 ≠ 乱码。 |
| **hybrid / 量化 KV** | 混合或量化的 KV 页语义；和稠密 bf16 不是同一套前提（S01 尤其重要）。 |
| **跨请求内容相同的乱码** | 多次独立请求得到的异常输出彼此相同（同一段垃圾重复出现），不是每次随机不同。常见于 S07。对照：各请求乱码各不相同（如 S45）。 |
| **内容相同计分** | 用「多条回复是否同一段文字」来估 precision 的做法；各请求内容不同时会低估（如 S45 记成 0）。 |
| **复现技巧** | 对外文档里「怎么跑才能对齐本包结论」的步骤与负载（旧称「复现配方」，已不用）。过程旧文称 **历史记录**，不称「历史配方」。 |
| **L1 / L2 定界** | **可选**粗标签（**不是** Transformer 层号；**不是**分析骨架）。优先不写；若写，仅作文末一行「定界停在哪」。**L1** = 检测停点；**L2** = 问题类停点——**仅当事实→推论已支撑到该类**才可标；否则写「尚未定界到… / 分析不出」，**不可**把构造已知根因贴成 L2。定界正文见 **定界写作标准**：事实 → 推论 → 结论。细定界仍走 [02](../02_problem_localization/README.md) **Q1–Q5**。包内尚未附对账时写「路径可用；归档尚未附结论」——**不要**因空 prompt / `KV?=否` 写「Q1–Q5 不适用」。 |

## 对外保留的 15 个典型案例

| ID | 包 | 结案结论 | 根因 | 现象 | 检测器 | trigger / precision / detect |
|----|-----|----------|------|------|--------|------------------------------|
| S01 | [cases/S01/](./cases/S01/) | FAIL（复现未出现） | KV 新块未置零（需 hybrid/量化 KV） | dense 未见坏输出 | 本轮无可检坏输出；非漏检结案 | 154 / 0† / 0 |
| S10′ | [cases/S10p/](./cases/S10p/) | PASS | FullAttn 回收块未清零 | 复读 / `xxxx` 塌缩 | `token_repeat` | 65 / 20 / 79 |
| S11 | [cases/S11/](./cases/S11/) | PASS | MLA RoPE pad-tail 错位 | digit / collapse 垃圾 | `token_repeat` | 138 / 39 / 60 |
| S07 | [cases/S07/](./cases/S07/) | FAIL+GAP | W8A8 dequant scale 崩溃 | 跨请求内容相同的乱码 | 期望 `logits_finite`→未检出；乱码检测漏检 | 2624 / 1 / 0 |
| S23 | [cases/S23/](./cases/S23/) | PASS | 一层 `o_proj` 权重置零 | 跨请求内容相同塌缩 | `token_repeat` | 2 / 17 / 48 |
| S45 | [cases/S45/](./cases/S45/) | FAIL+GAP | top-k 打在 −logits | 各不相同乱码 | 期望 `token_repeat`+`logits_finite`→未检出；乱码检测漏检 | 16 / 4 / 0 |
| S43 | [cases/S43/](./cases/S43/) | PASS | embedding ×100 | 换行塌缩 | `token_repeat` | 16 / 40 / 48 |
| S22 | [cases/S22/](./cases/S22/) | PASS | Spec resample 无独立 salt | acceptance_rate 塌缩 | `spec_acceptance`（主） | 126 / 0 / 47 |
| S06 | [cases/S06/](./cases/S06/) | PASS | MoE router bias / mask（构造） | 复读/乱码文本 | `token_repeat` | 70 / 1 / 1† |
| S26 | [cases/S26/](./cases/S26/) | PASS | RMSNorm fp32 错乘 | `1.1.1…` 复读 | `token_repeat` | 354 / 16 / 48 |
| S25 | [cases/S25/](./cases/S25/) | PASS | RoPE 后半维丢失 | `1.1.1…` / `1.0.0…` 复读 | `token_repeat` | 348 / 17 / 48 |
| S50 | [cases/S50/](./cases/S50/) | PASS | SwiGLU gate/up 对调 | 跨请求内容相同的 `!!!!` | `logits_finite` | 58 / 48 / 48 |
| S48 | [cases/S48/](./cases/S48/) | PASS | residual 极性取反 | 跨请求内容相同的 `!!!!` | `logits_finite` | 100 / 48 / 48 |
| S47 | [cases/S47/](./cases/S47/) | PASS | Attn 前 K/V 对调 | CJK / Trail 塌缩 | `token_repeat` | 58 / 37 / 48 |
| S33 | [cases/S33/](./cases/S33/) | PASS | softcap 缺 `*cap` rescale | `1.1.1…` 复读 | `token_repeat` | 130 / 17 / 48 |

计数摘自各包 `evidence/三层计数.json`（每个案例一份最新对外结果）。脚注：

- **S06 †**：detect 按归档 `token_repeat` report×1 记 **1**（与 `三层计数.json` / 跑批结果一致）；表内为数字，PASS 说明见 [cases/S06](./cases/S06/) 备注。
- **S07**：precision 记成 1，实为 48 次请求内容相同的乱码（以 samples + score 为准）。
- **S10′**：`precision=20` 可对照 `cases/S10p/evidence/samples/`（T181551）；detect=79 见 `evidence/reports/report_sample.json`。
- **S11**：`precision=39` 可对照 `cases/S11/evidence/samples/`（T190840）。
- **S23**：trigger=2 为 boot 置零（TP2 每卡一次），precision/detect 按请求计，故可 **precision > trigger**；结案看 detect=48。见 [cases/S23](./cases/S23/)。
- **S45**：`precision=4` 仍偏低估（各不相同乱码）；样本为准。复现技巧：双树写入 + temp=0.8 → **16 / 4 / 0**。
- **S22 / S25 / S26 / S33 / S45**：表内为现行 t/p/d；**trigger/precision 随并发浮动，detect 为判定口径**。复现要点见各包（S22：锚点脚本避 CRLF/LF；S25/S26：河名句×48 并发 + threshold=8；S33：双树 + 河名句）。
- **S01 †**：CJK / 早期脚本曾把通顺中文计成 precision 疑误判；现行 **排除 CJK 后 precision=0**；dense 满量 overlay trigger=154 仍无坏输出。见 [cases/S01/](./cases/S01/)。**与 S10′ 对照**：同属 KV 脏读族，但 S01 需 hybrid/量化 KV 才有目标症状；S10′ 在 dense FullAttn 回收路径上即可打出塌缩并被 `token_repeat` 检出。

`S10′` 在仓库里的目录名是 **`S10p`**。相关 Skills 见 [06](../06_agent_skills/)（**v5.9**）。

## 评估汇总（去刷分）

| 编号 | 文档 | 备注 |
|------|------|------|
| A6 | [guard-skills-evaluation-20261018.md](./guard-skills-evaluation-20261018.md) | 去刷分评估 + 作用分 ≈0.53（合并取代旧 raw / PR-weighted / 作用分三文） |

满量能力矩阵、mining 政策、verify-loop 等分析全文在内部仓 `runtime-guard-test/docs/`（需权限）；公开 `04` 只保留本 keep-set + 上述合并评估。

## 样本字段

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
- **report 里 prompt / `prompt_token_ids` 为空**：见名词表 **report 空 prompt**（hooks=false 跳过预缓存等；**不是**「clear 过早」独断说法）。旧归档可能仍为空；合 #19285 后同路径应非空。仍可用 samples **阅读**原文；**禁止**从字符串补造 ids 填进旧 report。空 ids **不**表示无 `block_ids`，也**不**表示不能做 KV 排除——走 **KV 排除定界**。包内无对账结果时写「路径可用；归档尚未附结论」，勿写「Q1–Q5 不适用」。
