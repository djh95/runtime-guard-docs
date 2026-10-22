# S48 · Residual negate（KV 不一致→定界）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 不一致→定界** |
| 检测 | **检出** |
| 三层率 | **100 / 48 / 48** |
| Detector | `logits_finite` |
| Origin | `both`（constructed） |
| Guard pin | G2 · `f2aefd068c4bd299d91cf0a1fdf642a3f327308f` |
| Run | 48_residual_negate-20261017T165947|

## 1 · 现象

跨请求内容相同的 `!!!!`；`logits_finite`×48。

## 2 · 根因

构造遵守 origin-faithful（禁止强制写 NaN / token fill）；细节见规格与 overlay。

fused add-RMSNorm 前 `residual = -residual`。不等于 S31 drop / S38 skip。

## 3 · Guard 结果

**检出。** **100 / 48 / 48**。结案档：**KV 不一致→定界**。

## 4 · 复现技巧

按本包 pin / 模型 / overlay 对齐三层率。

## 5 · 定界分析
### 事实

- 现象：非有限 logits / 异常输出（`evidence/samples/`）；detector：`logits_finite`（本包有检出）。
- KV 对比（`evidence/kv_compare.json`）：阈值 0.99；窗长≈14 且 **几乎全是 prompt**（无有效 output 槽 → 算不出「第一个输出 token 余弦」）。
- 摘要里写「idx=0 @ layer_36、min_cos=n/a」：实际是 **每个 token 的最小余弦都是 NaN**，脚本用 NaN 占「最差」——**不要**读成精确定位到第 0 个 token / 第 36 层（与 S07 同类写法）。

### 推断

- 只能记：**对不上 / 算不出有效余弦** → 还不能当「KV 已排除」；也还推不出「就是 prefill 第 0 个 token」。
- 要坐实首分歧 → 需重抓带足够 output 的配对 dump 再比。坏输出不可直接写成具体根因。

### 结论

- 结案档：**KV 不一致→定界**（现有对账摘要力度有限）。
- 尚未定界到具体写/传路径；分析不出 / 证据不足。

## 6 · 证据文件
| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格（Origin / 锚点 / overlay / knobs / 期望 detector） |
| `evidence/三层计数.json` | 三层明细（trigger / precision / detect） |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/samples/` | prompt + completion 样本 |
| `evidence/reports/` | Guard detector 报告 |
| `evidence/kv_compare.json` | 最新 KV 标杆对比摘要（余弦 / 首不一致 / 结论） |

## 7 · 上游 PR 关系
| PR / 链接 | 角色 |
|-----------|------|
| （constructed residual negate） | 无单一上游修复 PR |
