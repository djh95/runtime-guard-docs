# Runtime Guard 脱敏环境说明

本文只保留可公开提交的拓扑、容器角色、版本边界和核验清单。主机、账号、凭据、密钥、私有绝对路径和租户信息均使用占位符；实际值应存放在权限受限的本地交接文件中。

## 1. 拓扑和角色

| 环境 | 角色 | 加速卡逻辑视图 | 容器占位符 | 使用约束 |
|---|---|---:|---|---|
| 节点 A | 主线源码 import 与 Guard 兼容性 | 16×Ascend 910 逻辑设备 | `<GUARD_CONTAINER_A>` | 共享节点；每轮动态选择空闲卡 |
| 节点 B | 版本/import 差异与 Guard 兼容性 | 16×Ascend 910 逻辑设备 | `<GUARD_CONTAINER_B>` | 共享节点；必须显式固定源码 import |

连接信息使用：

```text
host: <GUARD_HOST_A|B>
user: <GUARD_SSH_USER>
credential: <LOCAL_SECRET_STORE_ONLY>
```

不得把真实值写入本仓。

## 2. 代码角色和版本

| 组件 | 节点 A | 节点 B |
|---|---|---|
| vLLM | editable 源码树，已核验短 SHA `ced6857` | 源码树 `6e448d0` 与 0.30.0 安装包并存；必须把正确源码置于 `PYTHONPATH` 首部 |
| vllm-ascend | 基线 `b64b4d714` 加未提交接线修改；必须记录 dirty diff 和文件校验值 | Guard 接线树 `3cec4f109`；另有无接线旧 checkout `b64b4d714`，不得从旧树目录启动 |
| runner | Model Runner v2 | Model Runner v2 |
| wiring 切换 | 可以测试“保留 wiring”和“无 wiring” | 使用固定 commit/worktree，不以目录名推断版本 |

每次启动前打印并保存：

```python
import sys, vllm, vllm_ascend
print(sys.path)
print(vllm.__file__)
print(vllm_ascend.__file__)
```

包版本号不能替代实际 import 文件、git SHA 和 dirty diff。

## 3. 模型兼容性摘要

2026-10-15 的 A 态（V2 + Guard 配置）矩阵覆盖 11 个目标模型：

- 9 个完成服务就绪、最小请求和同轮确定性检查；
- 2 个量化变体启动失败；当前摘要日志只有包装异常，不能据此断言根因；
- 该结果不包含完整 A/B/C，也不是 G0/G1/G2 性能结论。

公开结果只使用模型标识、TP、dtype、状态、冻结 SHA 和结果校验值；实际权重路径写作 `<MODEL_ROOT>/<MODEL_ID>`。

## 4. 启动占位符

```bash
export PYTHONPATH=<VLLM_SRC>:<VLLM_ASCEND_SRC>:$PYTHONPATH
export VLLM_USE_V2_MODEL_RUNNER=1
export VLLM_PLATFORM=ascend
export ASCEND_RT_VISIBLE_DEVICES=<VERIFIED_FREE_DEVICE_LIST>

cd <SAFE_LAUNCH_CWD>
python -m vllm.entrypoints.openai.api_server \
  --model <MODEL_ROOT>/<MODEL_ID> \
  --additional-config '{"runtime_config_path":"<RUNTIME_CONFIG_PATH>"}'
```

`runtime_config_path`、`runtime_dump_dir`、`runtime_report_dir` 是 additional-config 顶层键。不同产品版本支持的键集可能不同，必须以冻结版本的 schema 和最小解析测试为准。

## 5. 每轮环境/校验清单

### 硬件与系统

- 服务器匿名标识、Ascend 型号/数量、拓扑、NUMA；
- OS/kernel、固件、驱动、CANN；
- 设备健康、HBM、温度、功耗/频率和共享负载。

### 软件与容器

- Python、torch、torch_npu；
- vLLM、vllm-ascend 完整 SHA、dirty diff、编译参数和依赖锁；
- 容器 image digest；
- `sys.path` 和实际 import 文件。

### 模型与服务

- 模型 ID、权重/tokenizer 校验值、dtype、量化、最大长度；
- runner、TP/PP/DP/EP、端口占位符、环境变量和完整命令；
- V2 marker、所有 rank 日志、开始/结束时间和退出码。

### 存储与数据保护

- report/dump/log 目录写作 `<RUNTIME_OUTPUT_ROOT>`；
- 记录容量、inode、权限、配额、磁盘水位和保留策略；
- 默认 `save_sensitive_info=false`；
- 禁止提交权重、凭据、真实请求、KV dump 或未脱敏日志。

变体间任何未解释的环境指纹差异都会使配对性能轮次无效。
