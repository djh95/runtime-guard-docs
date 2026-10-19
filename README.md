# Runtime Guard 使用与定界手册

> **本目录不在 vllm-ascend 代码仓内。**  
> 面向：内部/外部开发、业务使用方、一线维护。  
> 目标：会启、会用、能抓现场、能做**问题初步定界**（不是根因定位工具链）。  
> **公开可读：** 启停手册、检测说明、**15 典型模版**、skills 契约（`06`，**v5.8**）。  
> **需内部仓权限：** 离线脚本 / FE / 满量 runs / 大体积分析矩阵 → **`runtime-guard-test`**（克隆后用本地路径；对外 HTTPS blob 会 404，勿当公开资源）。

## 读法（按角色）

| 角色 | 先读 | 再读 |
|------|------|------|
| 使用 / 运维启服 | [01 如何启动 Guard](./01_enable_and_start/README.md) | [03 检测算法](./03_detectors/README.md) 按需 |
| 一线维护 / 排障 | [01](./01_enable_and_start/README.md) → [02 问题定位分析](./02_problem_localization/README.md) | [04 实例](./04_case_studies/README.md)（15 短例 + `cases/Sxx` 完整包） |
| Agent / 自动化排障 | [06 Agent Skills](./06_agent_skills/README.md) | [02](./02_problem_localization/README.md) + 内部仓 `runtime-guard-test` 脚本 |
| 开发 / 算法理解 | [03 检测算法](./03_detectors/README.md) | 源码链接（文内 GitHub） |
| `releases/v0.30.0` / rc 线或不支持 Guard 的版本 | [05 版本 patch](./05_v030_backport/README.md) | 先对 BASE（见 CHANGELOG），再打 patch |

## 文档树

```text
README.md                          ← 本页（总目录）
01_enable_and_start/              ← ① 如何启动 Guard
02_problem_localization/          ← ② 问题定位分析（能力边界 + 流程）
03_detectors/                      ← ③ 检测算法（分文件）
04_case_studies/                   ← ④ 15 短例 + cases/Sxx 完整包（无私有空壳页）
05_v030_backport/                  ← ⑤ releases/v0.30.0 发布线 patch（持续更新）
06_agent_skills/                   ← ⑥ Skills v5.8 权威；test analysis/skill/ 为镜像
```

## 相对原思路的完善点

1. **启动与运维合一**：① 不只写命令，补路径/拓扑/热更/误区（一线最常踩坑）。  
2. **② 先讲清「能做什么 / 停在哪」**：定界 ≠ 定位；偶发抓现场 vs 必现但无标杆；输出交付模板。  
3. **③ 算法一文一 detector**：参数、阶段、误报/漏报、与 dump 的关系分开维护。  
4. **④ 实例与流程解耦**：流程稳定在 ②；公开 `04` = **15 短例 + 15×`cases/Sxx` 完整包**；满量 FE/runs/大矩阵只在私有 **runtime-guard-test**（公开不放「见 test」空壳）。  
5. **⑤ patch 可迭代**：`releases/v0.30.0` 发布线（含 `v0.30.0rc*`，无正式 `v0.30.0` tag）若需 Guard，须打对应 patch（BASE 见 [CHANGELOG](./05_v030_backport/CHANGELOG.md)）；更高版本先确认原生是否已支持。  
6. **⑥ Agent Skills**：与产品 detector / 热更 / 脚本仓对齐的可执行排障编排；人读仍以 ② 为准。

## 上游产品文档（GitHub）

| 文档 | URL |
|------|-----|
| Runtime Guard 功能说明 | https://github.com/vllm-project/vllm-ascend/blob/main/docs/source/user_guide/feature_guide/runtime_guard.md |
| runtime_config 字段参考 | https://github.com/vllm-project/vllm-ascend/blob/main/docs/source/user_guide/configuration/runtime_config.md |
| additional_config · runtime_guard | https://github.com/vllm-project/vllm-ascend/blob/main/docs/source/user_guide/configuration/additional_config.md#runtime_guard |
| 功能合入 PR | https://github.com/vllm-project/vllm-ascend/pull/16849 |
| 性能与鲁棒增强 PR | https://github.com/vllm-project/vllm-ascend/pull/18644 |
| `v0.30.0rc1` 标签（示例；无 `v0.30.0` 正式 tag） | https://github.com/vllm-project/vllm-ascend/releases/tag/v0.30.0rc1 |
| `releases/v0.30.0` 分支 | https://github.com/vllm-project/vllm-ascend/tree/releases/v0.30.0 |

## 一句话能力边界

Runtime Guard **能**：在线检出异常类、落 JSON 报告、可选 dump KV、在有标杆时做 KV 首分歧定界。  
Runtime Guard **不能**：替代调试器定位到具体算子、代码提交点；在**无清洁标杆**时无法完成「buggy vs ref」层/token 细粒度定界；无法对 hang/OOM/拓扑错误做根因定界。
