# ④ 问题定位实例分析

> **状态：占位，后续按案例补充。**  
> 流程与能力边界以 [02_problem_localization.md](../02_problem_localization.md) 为准；本目录只放「真实故事 + 证据路径」。

## 写作模板（每案一篇）

建议文件名：`YYYYMMDD_<short_title>.md`

```markdown
# 案例：<一句话现象>

## 元信息
- 日期 / 环境 / 模型 / 拓扑 / MODE
- 版本：main 某 commit 或 v0.30 + patch 包版本（见 05 CHANGELOG）
- 是否有标杆：有 / 无

## 现象
- 业务侧描述、复现率、是否必现

## Guard 配置
- 启动参数摘要 + detector 片段（可贴 JSON）

## 抓取结果
- report 路径（或脱敏摘要）
- dump 是否齐全（tp 列表）

## 定界结论（用 02 交付模板）
- 粘贴【定界】段落
- 明确写：未定位到算子/提交

## 若无标杆
- 停在哪一步、还缺什么对照环境

## 后续
- 开发跟进项 / 是否已关闭
```

## 计划补充的方向（示例标题，未写正文）

| 编号 | 拟标题 | 备注 |
|------|--------|------|
| C1 | 偶发复读：`token_repeat` + dump，有标杆首分歧 | 待补 |
| C2 | 必现乱码但无清洁标杆：仅 logits/report 定界 | 强调 §2.3 |
| C3 | Spec 接受率骤降 | 需 MTP 环境 |
| C4 | PP/TP 找错 rank 导致「无报告」误判 | 运维向 |
有真实案例时，在本表加链接到同目录新文件即可。

## 已补充（与 `runtime-guard-test` 同步）

| 编号 | 文档 | 备注 |
|------|------|------|
| A1 | [anomaly-skills-capability-20261017.md](./anomaly-skills-capability-20261017.md) | PASS/FAIL+GAP 能力矩阵 |
| A2 | [anomaly-skills-verify-loop-20261017.md](./anomaly-skills-verify-loop-20261017.md) | analyze→edit→re-verify before→after |
| A3 | [anomaly-skills-handoff.md](./anomaly-skills-handoff.md) | 160→skills inbox / IDLE |
| A4 | [anomaly-skills-analysis-20261017.md](./anomaly-skills-analysis-20261017.md) | 分析纪要 |
| A5 | [anomaly-skills-runs/](./anomaly-skills-runs/) | 逐场景 + batch-pass-wave |
| A6 | [guard-skills-evaluation-pr-weighted-20261018.md](./guard-skills-evaluation-pr-weighted-20261018.md) | **PR-weighted 评估头条**（A∪B；C 不计入实力） |
| A7 | [anomaly-mining-policy-pr-rooted-20261018.md](./anomaly-mining-policy-pr-rooted-20261018.md) | PR-rooted / typed / 停 soft-inv 刷分 |
| A8 | [guard-skills-evaluation-20261017.md](./guard-skills-evaluation-20261017.md) | raw 全量附录（含被刷分抬高的数字） |

Skill 手册副本：[06_agent_skills/](../06_agent_skills/)（对齐 `runtime-guard-test/analysis/skill/` **v5.8**）。
