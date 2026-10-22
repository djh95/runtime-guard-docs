# S47 · Attn K/V swap

公开案例包（**尚未实测归档**）。本目录只保留构造材料；**无** samples / reports / 三层 / 跑批 / KV 对账。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | （空 · 尚未实测） |
| 检测 | （空） |
| 三层率 | （空） |
| Detector（期望） | `token_repeat` |
| Origin / 构造 | 见 [evidence/规格说明.md](./evidence/规格说明.md) |
| Guard pin | （空） |
| 模型 / Run | （空） |

## 1 · 现象

（空 · 尚未实测，无样本）

## 2 · 案例背景 / 构造

Attn 前 K/V 对调。细节与 knobs 见 [evidence/规格说明.md](./evidence/规格说明.md)；补丁见 [evidence/overlay.patch](./evidence/overlay.patch)。

## 3 · Guard 结果

（空 · 尚未实测，无 report）

## 4 · 复现技巧

见规格说明中的 knobs / 环境要求。按规格构造环境后实测，再回填钉点与证据。

## 5 · 定界分析

### 事实

（空）

### 推断

（空）

### 结论

（空 · 尚未实测）

## 6 · 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格（Origin / 锚点 / overlay / knobs / 期望 detector） |

## 7 · 上游 PR 关系

见 [evidence/规格说明.md](./evidence/规格说明.md)（若有锚点）。本 README 不重复实测结论。
