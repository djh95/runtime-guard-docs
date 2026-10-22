# S48 · Residual negate（复现未抓到）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **复现未抓到** |
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

**检出。** **100 / 48 / 48**。结案档：**复现未抓到**。

## 4 · 复现技巧

按本包 pin / 模型 / overlay 对齐三层率。

## 5 · 定界分析

### 事实

- 现象 / 检测见上文钉点与 samples（或 reports）。
- **有效 KV 对账：无。** 本包曾归档的 `kv_compare.json` 及其中「首不一致 / 层号 / 余弦」结论**全部撤回**（新旧跑次混用、空 prompt、弱窗、全 NaN 占位等问题，不可信）。

### 推断

- 在重做**同一次异常请求**的有效异常 dump ↔ 标杆对账之前，**不能**得出「排除 KV」或「KV 不一致定界」。
- 坏输出 / 构造预期 ≠ 已证根因。

### 结论

- 结案档：**复现未抓到**（有异常或检出证据，但无有效异常 KV 可对账）。
- **尚未做有效 KV 对账**；分析不出 / 证据不足。


## 6 · 证据文件
| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格（Origin / 锚点 / overlay / knobs / 期望 detector） |
| `evidence/三层计数.json` | 三层明细（trigger / precision / detect） |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/samples/` | prompt + completion 样本 |
| `evidence/reports/` | Guard detector 报告 |

## 7 · 上游 PR 关系
| PR / 链接 | 角色 |
|-----------|------|
| （constructed residual negate） | 无单一上游修复 PR |
