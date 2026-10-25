# S60 · PD 类中段槽污染（金标 A · 完整）

公开案例包。Prefill 写完后在首 decode：（1）negate **prompt 中段槽**；（2）对新建 decode 槽做 target-cos≈0.8 正交混合。KV 对账呈现「中段坏 → 后续 prompt 又≈1 → out[0] 自 L0 起≈0.8」链，专供定界金标 A 教学。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 不一致→定界** |
| 检测 | **检出** |
| 三层率 | **6056 / 29 / 48**（触发 / 判坏 / 报告；48 请求；trigger 含各层 mid+out0 打点） |
| Detector | `token_repeat` |
| Origin | PD 类 post-prefill 中段污染 + 首 decode 新槽 soft 污染（构造匹配；非真 Mooncake 1P1D） |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) |
| 模型 | Qwen3-8B · TP2 |
| Run | `keep-set-retest-20261022` · `S60-layers-20261024T231455` / dump `S60-pr19285-20261024T231807` |
| 金标 | **A 完整命中**（坏→恢复 + out[0] 早层 `model.layers.*` ≈0.8） |

## 1 · 现象

约 29/48 判坏；重复-token 检测命中。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 案例背景 / 构造

首 decode 时：对已写完的 prompt 中段槽（默认 token 5）K/V 取反；并对首次写入的 decode 槽做确定性正交混合使余弦≈0.8（能量布局无关；禁 NaN/fill）。清洁对照无 overlay。细节见 [evidence/规格说明.md](./evidence/规格说明.md)。

## 3 · Guard 结果

**检出。** **6056 / 29 / 48**。结案：**KV 不一致→定界**——无数问题；表1 可见中段坏后多个 prompt 恢复≈1；out[0] 自 L0 起≈0.8。

## 4 · 复现技巧

| 项 | 怎么做 |
|----|--------|
| Overlay | `evidence/overlay.patch`（`60_pd_mid_slot_pollute_v3`） |
| 模型 | Qwen3-8B TP2 |
| detector | `token_repeat` |
| 对照 | 清洁树 force-feed 报告 token id |

## 5 · 定界分析

### 事实

- **清洁标杆（≥2 组）：** 同波 clean-ref；shape 一致（`[1,128,4,128]`）。
- **两对同向：** 均无数值问题；首坏均在 **prompt[5]**（cos≈−1）；prompt[6…] 最差格回到≈1。
- **有效槽 / 未用槽：** 有效槽有限、无 NaN/Inf（`S60.kv_finite_unused.json`）。未用槽：异常侧有**有限非零残留**（卫生）；代表对标杆未用可为全 0——**勿写「未用一定填 0」**。
- **out[0]：** `model.layers.0`… 早层余弦 **≈0.80**（两对一致，见表2）；与金标「从第一层起≈0.8」对齐。表1 最差格可能落在杂层名（更低）——定界以 `model.layers.*` 为准。
- **仅 PD：** 本钉点 = overlay 武装的 PD **类**时序；清洁无 overlay 为对照。真 1P1D / Mooncake 未在本包拓扑验证。
- 证据：`evidence/S60.full_tables.json`（**.pt** 在 builder 机耐久 `verified_kv/S60/`）。

### KV 对账表

分桶：`≈1`≥0.99；`0.9–0.99`；`0.8–0.9`；…；`<0.1`。

**代表对**（`req_id`=`cmpl-96783d9281bf1fc9-0-809f042d`；`n_prompt=15`；对比窗 `n_tokens=24` → out[0]…out[8]；全窗见 `S60.full_tables.json`）。

**表1 · 每 token 最差格**（首坏后 out 一并列出）

| token 序号 | 角色 | 该 token 最差格 |
| --- | --- | --- |
| 0–4 | prompt[0–4] | ≈1 |
| 5 | prompt[5] | <0.1（最差 L0，cos≈−1） |
| 6–14 | prompt[6–14] | ≈1（恢复） |
| 15 | out[0] | 表1 最差 0.3–0.6（杂层）；`model.layers.*` 早层≈0.8（见**表2**） |
| 16 | out[1] | 0.1–0.3（min_cos≈0.14 @ L33） |
| 17 | out[2] | 0.3–0.6（min_cos≈0.37 @ L17） |
| 18 | out[3] | 0.1–0.3（min_cos≈0.25） |
| 19–23 | out[4]–out[8] | 多为 <0.1～0.1–0.3（金标链在 out[0] 已钉；后续 out 仍坏） |

**表2 · out[0] 逐层（`model.layers.*`，代表对）**

| 层 | cos（约） |
| --- | --- |
| L0–L20 | ≈0.80 |
| L30–L35 | ≈0.74–0.79 |

（prompt[5] 全层≈−1；与「只脏中段槽」一致。）

### 推断

1. prompt[5] 在写 cache 时算对（其后 prompt 又≈1）→ **之后**该槽被污染。
2. out[0] 自 L0 起≈0.8 → 符合「prefill 后 / decode 前（类）交接污染」教学形态。
3. 无数问题 → 定界走余弦时序，不走有限性门闩。
4. 真 Mooncake 1P1D 仍未跑——根因不能写死到某传输 PR。

### 结论

**KV 不一致→定界**；教学点 = **金标 A 完整**（坏→恢复 + out0 早层≈0.8）。真 PD 拓扑复现仍为已知缺口，已写进事实，不拔高。

## 6 · 证据

- `evidence/overlay.patch`
- `evidence/S60.full_tables.json` · `S60.kv_pairs_recap.json` · `S60.kv_finite_unused.json`
- `evidence/reports/` · `evidence/samples/`

## 7 · 上游 / 类比

无单一合并 PR 锚点；故障类比 PD reformat / KV 交接写歪。本包为 **origin-faithful 时序构造**，不是某 PR 的逐行反修。
