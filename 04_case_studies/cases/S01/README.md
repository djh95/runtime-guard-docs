# S01 · 新 KV block 未置零（KV 一致→排除 KV · dense）

公开案例包。本窗在 **稠密（dense）Qwen3-8B** 上跑：**不是**规格目标形态（目标要 hybrid / 量化 KV 脏读）。这里是数字复读被检测抓住，但对账说明坏值**没有**走 KV 主因路径。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 一致→排除 KV**（异常与干净对照的 KV 对得上） |
| 检测 | **检出**（Guard 打出了报告） |
| 三层率 | **82 / 16 / 48**（触发 / 判坏 / 报告；`token_repeat`×48） |
| Detector | `token_repeat`（抓「同一 token 反复出现」） |
| Origin | 见规格 |
| Guard pin | G2 `f2aefd068`；抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285)（让 prompt token 列表非空） |
| 模型 | Qwen3-8B dense · TP2 · CARD=4,5 · `192.168.13.160` / `rg-test-160` |
| Run | `keep-set-retest-20261022` · `S01-layers-20261023T125812` |

## 1 · 现象

部分请求变成数字复读（如 `1.1.1…`，约 16/48）；**多数样本仍是通顺英文**。靠重复-token 检测抓住。样本见 [evidence/samples/](./evidence/samples/)。规格目标形态更常看 logits 是否非有限——本窗不是那种。

## 2 · 案例背景 / 构造

构造意图：新分配的 KV 块跳过清零。细节见 [evidence/规格说明.md](./evidence/规格说明.md)。**hybrid / 量化 KV 前提本轮未满足；不要把 dense 复读当成目标脏读乱码已复现。**

## 3 · Guard 结果

**检出。** 三层 **82 / 16 / 48**。结案：**KV 一致→排除 KV**——对账无数值崩溃，与干净对照的相似度（余弦）全程干净（见下节事实）。

## 4 · 复现技巧

| 项 | 怎么做 |
|----|--------|
| Overlay | `01_kv_block_nonzero.patch` |
| 模型 | Qwen3-8B dense（本轮） |
| 负载 | 变长 pad 搅动缓存 · 并发 48 |
| detector | `token_repeat` |

## 5 · 定界分析

### 事实

- **清洁标杆（≥2 组）：** 用同一段 history，在**未打 overlay 的干净服务**上重放抓 KV 作对照。本包 **2 组**；两边 shape 一致（`[1,128,4,128]`）。对比窗含 prompt+生成（本窗约 `n_prompt=14`，history 按 `p+o−1`，对账长度约 21）。
- **两对同向：** 两对都是「有效槽无数值问题、余弦全程干净」。
- **有效槽 / 「格」：** 有效槽 = 请求真正用到的 KV；「某一 token × 某一层」算一格。本窗数值问题格 **0**；也没有「第一处余弦分叉」。
- **未用槽：** 异常侧有些位置是有限非 0——叫**卫生脏写**（常见、通常不单独造成坏输出），不是本窗定界依据。
- **提醒：** 这是 **dense** 窗结论；规格目标的 hybrid/量化 KV 脏读形态本轮未测。
- 证据：`evidence/kv_*.json`（**.pt 未入库**）。

### 推断

- 有效对账匹配 → **排除「坏值经/进 KV」为主因**（仅对本 dense 窗）。
- 不推广到 hybrid / 量化形态。

### 结论

- 结案档：**KV 一致→排除 KV**（dense；两组同向）。

## 6 · 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的补丁 |
| `evidence/规格说明.md` | 怎么构造 / 本轮实测摘要 |
| `evidence/三层计数.json` / `跑批结果.json` | 三层数字与结案摘要 |
| `evidence/samples/` / `reports/` | 输出样本 / 检测报告 |
| `evidence/kv_*.json` | KV 对账摘要（**.pt 不进库**） |

## 7 · 上游 PR 关系

见规格（#43990 / #47574）。
