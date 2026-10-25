# Runtime Guard 使用与定界手册

> **本目录不在 vllm-ascend 代码仓内。**  
> 面向：内部/外部开发、业务使用方、一线维护。  
> 读完你能**启动和使用** Guard、**抓到异常现场**，并能做**初步定界**——它不是根因定位工具。  
> **公开可读：** 启停手册、检测说明、`04` 对外保留的约 **15** 个典型案例（keep-set）+ [短词汇表](./04_case_studies/词汇表.md)、skills 契约（`06`）。  
> **离线脚本：** 本仓 [`06_agent_skills/scripts/`](./06_agent_skills/scripts/)。  
> **完整评测矩阵不在本仓**（满量失败证据包 / runs / 大体积分析矩阵需内部评测仓权限）。

## 读法（按角色）

| 角色 | 先读 | 再读 |
|------|------|------|
| 使用 / 运维启服 | [01 如何启动 Guard](./01_enable_and_start/README.md) | [03 检测算法](./03_detectors/README.md) 按需 |
| 一线维护 / 排障 | [01](./01_enable_and_start/README.md) → [02 问题定位分析](./02_problem_localization/README.md) | [04 实例](./04_case_studies/README.md) |
| Agent / 自动化排障 | [06 Agent Skills](./06_agent_skills/README.md) | [02](./02_problem_localization/README.md) + [`06/.../scripts/`](./06_agent_skills/scripts/) |
| 开发 / 算法理解 | [03 检测算法](./03_detectors/README.md) | [07 架构 UML 十四图](./07_architecture/guard-runtime-config-uml-14.md) |
| `releases/v0.30.0` × **MRV2**（Model Runner v2，现行执行器的 Guard **适配补丁包**） | [05_v030 MRV2](./05_v030_backport/README.md) | skill `apply-v030-mrv2-patch`；BASE 见 CHANGELOG |
| 历史/常用 release × **MRV1**（Model Runner v1 的适配补丁包；含 v0.30 MRV1） | [05_mrv1 MRV1](./05_mrv1_backport/README.md) | skill `apply-mrv1-patch`；与 05_v030 **两个补丁不能同时打**（见词汇表「叠打」） |

## 文档树

```text
README.md                          ← 本页（总目录）
01_enable_and_start/              ← ① 如何启动 Guard
02_problem_localization/          ← ② 问题定位分析（能力边界 + 流程）
03_detectors/                      ← ③ 检测算法（分文件）
04_case_studies/                   ← ④ 典型案例 ~15×cases/Sxx/ + 索引 + 短词汇表
05_mrv1_backport/                  ← ⑤ 支持 MRV1（多 release 接线）
05_v030_backport/                  ← ⑤ 支持 0.30 MRV2（仅 V2）
06_agent_skills/                   ← ⑥ Skills 权威
07_architecture/                   ← ⑦ 架构 UML（Guard + runtime_config 十四图）
```

## 相对原思路的完善点

1. **启动与运维合一**：① 不只写命令，还补路径/拓扑/热更/误区（一线最常踩坑）。  
2. **第②章先讲能力边界**：定界不等于定位；偶发问题用热更抓现场，稳定复现但没有对照服务的按 §2.3 处理，有对照再走十问。  
3. **③ 算法一文一 detector**：参数、阶段、误报/漏报、与 dump 的关系分开维护。  
4. **④ 实例与流程解耦**：流程稳定在 ②；公开 `04` = 约 **15** 个完整案例包 + 索引；证据在包内 `evidence/`。  
5. **⑤ 两份适配补丁包**：MRV1 → [`05_mrv1_backport`](./05_mrv1_backport/)；0.30 MRV2 → [`05_v030_backport`](./05_v030_backport/)。更高版本先确认原生是否已支持。  
6. **⑥ Agent Skills**：排障五件套 + 两个适配补丁 skill；**人类读者仍以 ② 为准**（skills 主要面向 agent）。

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

Runtime Guard **能**：在线检出异常类、落 JSON 报告、可选 dump KV；有**未打故障补丁的对照服务**时，可把异常侧与对照侧的 KV 逐层对比，找第一个对不上的位置。  
Runtime Guard **不能**：替代调试器定位到具体算子、代码提交点；没有对照服务时做不了这种细粒度对比；无法对 hang/OOM/拓扑错误做根因定界。

跨页术语（keep-set、对账、有效槽、结案四档、叠打等）：[短词汇表](./04_case_studies/词汇表.md)。
