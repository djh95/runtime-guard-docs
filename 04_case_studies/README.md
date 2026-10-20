# ④ 问题定位实例分析

定位流程以 [02 问题定位](../02_problem_localization/README.md) 为准。

这里放的是**对外保留的 15 个典型案例**：每个案例自己一套材料。

每个案例只有：

- **`README.md`**：一篇讲完（现象 → 根因 → Guard 结果 → 复现技巧 → 教学要点 → evidence 文件表 → 上游 PR 关系）
- **`evidence/`**：样本、三层计数、WHY、overlay / reports 等证据

包结构约定见同目录下各 `cases/Sxx/`；标准一页摘要在 Project store 的 `docs/04-case-package-standard-20261020.md`。

## 名词怎么读（先看这里）

| 说法 | 含义 |
|------|------|
| **PASS** | 异常按预期出现，且期望的 detector **命中**（有 report）。 |
| **FAIL** | 未达到 PASS 的总称（复现没出来，或复现出来了但没检出，都算 FAIL）。 |
| **GAP** | **检测能力缺口**这种问题类型（例如只抓 NaN、抓不住有限乱码）。是缺口分类，不是单独一种「跑失败」标签。 |
| **FAIL+GAP** | 结论标签：异常（或目标坏输出）**已经出现**，但 detector **没检出**——既记未过关（FAIL），又标成检测缺口（GAP）。**有异常是前提**；没有异常出现时不要写 FAIL+GAP。 |
| **复现失败** | 打了 patch / overlay，但目标异常**没有出现**。不要写 GAP。结论记 **FAIL**，并注明原因（形态不对、注入未打中、负载不够、patch 未真正生效等）。可简称 **FAIL（复现未出现）** / **repro-blocked**。 |
| **结案结论** | 写在案例上的判定标签（PASS / FAIL+GAP / FAIL（复现未出现）等），标明是否按预期复现并检出。 |
| **样本** | 保存的请求 / 回复证据；应含 prompt + 输出，用来核对坏没坏、是否误判。 |
| **三层计数** | **trigger**（注入路径打中次数）/ **precision**（输出被判异常的次数，≠ 模型精度）/ **detect**（Guard 报告命中次数）。三者不相等；见各包 `layers.json` 等。 |
| **layers.json** | 三层明细（trigger / precision / detect、备注、detector 名等）。索引表数字通常摘自这里。 |
| **status.json** | 跑批元数据 + 结案摘要（场景名、verdict、模型、run 路径、三层摘要）。和 `layers.json` 一起读。 |
| **WHY**（`WHY_PASS` / `WHY_UNDETECTED` 等） | 对本案例结果的简短说明：为什么过关，或为什么没检出 / 没复现。 |
| **overlay / overlay.patch** | 制造异常用的代码补丁；完整补丁在 evidence，摘录在 `SPEC_excerpt.md`。 |
| **上游锚点** | 本案例所对照的**上游修复 PR / issue**（「原 bug 是在哪修好的」）。多笔时要标明：根因修复 / 同族相关 / 对照 cousin，不要堆一串无说明链接。 |
| **Origin**（字段） | 案例表格里的 **`Origin`** 标的是**异常逻辑落在哪棵代码树**，取值只有三种：`vllm-only`（只改 / 只坏在上游 vLLM）、`ascend-only`（只改 / 只坏在 Ascend 插件树）、`both`（两边同失败模式，或复现要动双树）。它**不是**「有没有忠实复现」、也不是 PR 好坏分。旁注里的 `constructed` 只说明注入是按该类故障构造的，不改变上述三值。 |
| **origin-faithful** | **复现纪律**：注入要忠于原 bug 逻辑；禁止强制写 NaN、填复读 token 等「伪造症状」。与上表 **Origin 字段**是两件事。文档里**没有**「origin bath」；若看到多半是口误，应指 **origin-faithful** 或 **Origin**。 |
| **CJK** | **中日韩字符**（Chinese / Japanese / Korean）。旧评分曾把「含非 ASCII 的中文」当成 `garbage_mixed_script`，把通顺中文误计成 precision——尤其 S01。现行规则：**排除 CJK 后再计 weird**；通顺中文 ≠ 乱码。 |
| **hybrid / 量化 KV** | 混合或量化的 KV 页语义；和稠密 bf16 不是同一套前提（S01 尤其重要）。 |
| **跨请求内容相同的乱码** | 多次独立请求得到的异常输出彼此相同（同一段垃圾重复出现），不是每次随机不同。常见于 S07。对照：各请求乱码各不相同（如 S45）。 |
| **内容相同计分** | 用「多条回复是否同一段文字」来估 precision 的做法；各请求内容不同时会低估（如 S45 记成 0）。 |
| **复现技巧** | 对外文档里「怎么跑才能对齐本包结论」的步骤与负载（旧称「复现配方」，已不用）。过程旧文称 **历史记录**，不称「历史配方」。 |

## 对外保留的 15 个典型案例

| ID | 包 | 结案结论 | 根因 | 现象 | 检测器 | trigger / precision / detect |
|----|-----|----------|------|------|--------|------------------------------|
| S01 | [cases/S01/](./cases/S01/) | FAIL（复现未出现） | KV 新块未置零（需 hybrid/量化 KV） | dense 未见坏输出（旧 precision 为 CJK 误计） | 本轮无可检坏输出；非漏检结案 | 154 / 0† / 0 |
| S10′ | [cases/S10p/](./cases/S10p/) | PASS | FullAttn 回收块未清零 | 复读 / `xxxx` 塌缩 | `token_repeat` | 65 / 20† / 79 |
| S11 | [cases/S11/](./cases/S11/) | PASS | MLA RoPE pad-tail 错位 | digit / collapse 垃圾 | `token_repeat` | 138 / 39 / 60 |
| S07 | [cases/S07/](./cases/S07/) | FAIL+GAP | W8A8 dequant scale 崩溃 | 跨请求内容相同的乱码 | 期望 `logits_finite`→未检出；乱码检测漏检 | 2624 / 1 / 0 |
| S23 | [cases/S23/](./cases/S23/) | PASS | 一层 `o_proj` 权重置零 | 跨请求内容相同塌缩 | `token_repeat` | 2 / 17 / 48 |
| S45 | [cases/S45/](./cases/S45/) | FAIL+GAP | top-k 打在 −logits | 各不相同乱码 | 期望 `token_repeat`+`logits_finite`→未检出；乱码检测漏检 | 16 / 4 / 0 |
| S43 | [cases/S43/](./cases/S43/) | PASS | embedding ×100 | 换行塌缩 | `token_repeat` | 16 / 40 / 48 |
| S22 | [cases/S22/](./cases/S22/) | PASS | Spec resample 无独立 salt | acceptance_rate 塌缩 | `spec_acceptance`（主） | 126 / 0 / 47 |
| S06 | [cases/S06/](./cases/S06/) | PASS | MoE router bias / mask | 进错专家、复读文本 | `token_repeat` | 70 / 1 / 1† |
| S26 | [cases/S26/](./cases/S26/) | PASS | RMSNorm fp32 错乘 | `1.1.1…` 复读 | `token_repeat` | 354 / 16 / 48 |
| S25 | [cases/S25/](./cases/S25/) | PASS | RoPE 后半维丢失 | `1.1.1…` / `1.0.0…` 复读 | `token_repeat` | 348 / 17 / 48 |
| S50 | [cases/S50/](./cases/S50/) | PASS | SwiGLU gate/up 对调 | 跨请求内容相同的 `!!!!` | `logits_finite` | 58 / 48 / 48 |
| S48 | [cases/S48/](./cases/S48/) | PASS | residual 极性取反 | 跨请求内容相同的 `!!!!` | `logits_finite` | 100 / 48 / 48 |
| S47 | [cases/S47/](./cases/S47/) | PASS | Attn 前 K/V 对调 | CJK / Trail 塌缩 | `token_repeat` | 58 / 37 / 48 |
| S33 | [cases/S33/](./cases/S33/) | PASS | softcap 缺 `*cap` rescale | `1.1.1…` 复读 | `token_repeat` | 130 / 17 / 48 |

计数摘自各包 `evidence/layers.json`（或归档已公布数）。脚注：

- **S06 †**：`layers.json` / status 写 `detect_reports=0`，但同次归档有 `token_repeat` report×1；表内 detect 按 report 记 **1**。
- **S07**：precision 记成 1，实为 48 次请求内容相同的乱码（以 samples + score 为准）。
- **S10′ †**：`precision=20` 仅来自 `layers.json` 计数；本仓曾长期无 prompt+completion 样本；detect=79 现有 `evidence/reports/report_sample.json`。
- **S45**：`precision=4` 仍偏低估（各不相同乱码）；样本为准。复现技巧：双树写入 + temp=0.8 → **16 / 4 / 0**。
- **S22 / S25 / S26 / S33**：表内为现行 t/p/d；复现要点见各包（S22：锚点脚本避 CRLF/LF；S25/S26：河名句×48 并发 + threshold=8；S33：双树 + 河名句）。
- **S01 †**：CJK 排除后 **precision=0**；dense 满量 overlay trigger=154 仍无坏输出。见 [cases/S01/](./cases/S01/)。**与 S10′ 对照**：同属 KV 脏读族，但 S01 需 hybrid/量化 KV 才有目标症状；S10′ 在 dense FullAttn 回收路径上即可打出塌缩并被 `token_repeat` 检出。

`S10′` 在仓库里的目录名是 **`S10p`**。相关 Skills 见 [06](../06_agent_skills/)（**v5.8**）。

## 样本字段

`evidence/` 里的样本 JSON 使用：

```json
{
  "prompt": "请求原文",
  "completion": "模型输出文本",
  "api_response": { }
}
```

`api_response` 是原始 `/v1/completions` 响应（可选但建议保留）。只看 `completion` 不够——对照时要连 prompt 一起看。
