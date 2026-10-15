# Runtime Guard 验证任务流程

本文给出可审计的执行顺序，并明确区分兼容性、功能和性能证据。

## 1. 冻结对象

执行前记录 docs、test、vLLM、vllm-ascend 的 remote、branch、完整 HEAD、dirty diff、依赖版本和容器镜像 digest。每次结果必须绑定：

- 时间、模型、并行拓扑和 runner；
- 完整启动命令、配置和可见设备；
- `sys.path`、`vllm.__file__`、`vllm_ascend.__file__`；
- 原始日志、退出码、结果文件与 SHA256。

PR 描述和历史报告只能作为待复核声明；当前冻结 manifest 与原始证据优先。

## 2. 预检和功能顺序

1. 只读检查设备健康、目标卡 HBM、共享负载、端口、残留进程、磁盘、目录权限和模型可读性。
2. 强制使用 Model Runner v2；日志缺少 v2 marker 时中止并作废该轮数据。
3. 每模型执行三态：
   - A：V2 + Guard 配置；
   - B：保留 Guard wiring，不传 additional-config；
   - C：无 Guard wiring 的真实基线。
4. 先跑 CPU UT 和配置解析，再做最小启动、确定性请求、detector 正负路径、report/dump 契约和 hot reload。
5. hot reload 必须证明 `off→不触发、on→产生新 report、off→再次不触发`；只看到配置文件变化不算通过。
6. 普通 report/dump I/O 故障应隔离；collective/rank 错误必须显式失败。

## 3. 三版本性能矩阵

| 变体 | 固定定义 | 验证目的 |
|---|---|---|
| G0 | PR #16849 第一笔功能提交的直接父提交，无 Guard 代码/接线 | no-guard 基线 |
| G1 | 仅 PR #16849 最终合入内容，默认关闭 | 功能引入成本 |
| G2 | G1 叠加 PR #18644 的冻结待测 head，默认关闭 | static-idle/鲁棒性修复 |

三变体优先使用同一可运行 vLLM commit、镜像、依赖、模型、参数和输入。若 vLLM SHA 不同，结果只能用于兼容性说明，不能归因于 Guard。

采用平衡交错冷启，至少完成：

1. `G0→G1→G2`
2. `G1→G2→G0`
3. `G2→G0→G1`

主门禁为 G1/G0、G2/G0 的稳态 output throughput paired ratio 95% CI 下界不低于 `0.999`，并同时报告延迟、错误率、RSS/HBM 和 token 一致性。点估计通过但区间不足时，结论是“统计不确定”。

## 4. 当前证据边界（2026-10-15）

- [#16849](https://github.com/vllm-project/vllm-ascend/pull/16849) 已合并；功能是 v2-only、默认关闭，包含配置、三个 detector、report 与 KV dump。
- [#18644](https://github.com/vllm-project/vllm-ascend/pull/18644) 当前为 open，2026-10-15 核验 head 为 `a60cf420735b7c675469999096d093c942dfbd2f`；每次 G2 执行前仍须重新冻结状态、head 和 diff。
- 最新兼容性矩阵中，11 个目标模型有 9 个完成 A 态启动和确定性请求；两个量化变体启动失败，首个 worker 根因仍需补采。
- 上述 9/11 不是完整 A/B/C，也不是 G0/G1/G2 性能验收。
- 历史 A/B/A/B/A 结果使用 V1，且变体定义不等于 G0/G1/G2，不纳入性能门禁。
- main 优先；v0.30 回迁与性能必须独立验证。

## 5. 收口

- 文档陈述标记为代码、UT、实机、设计声明或过期证据。
- 公开材料只保留脱敏环境拓扑、角色和核验清单。
- 最终从空 shell 按 README 演练；仅引用冻结 manifest 中的结果。
