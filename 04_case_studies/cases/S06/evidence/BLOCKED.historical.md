# S06 — 历史 BLOCKED（setup，不是 FAIL）

## 根因

在当时的 Guard pin / CANN 栈上，可用空闲 NPU HBM 条件下，很难拉起一个健康的 MoE boot：

1. **DeepSeek-V2-Lite / Moonlight-16B-A3B**：启动死在  
   `RuntimeError: aclnnAddRmsNormBias ... not in libopapi.so`  
   （该镜像上的 CANN / opapi 缺口）。
2. **Qwen3-30B-A3B** TP2：load 过程中被 **OOM-killed**（runner 日志里是 `Killed`）——空闲 HBM 不够同时扛 MoE 权重和 KV。

## 归类

**setup / BLOCKED**：overlay 从未在活着的 server 上被真正跑过。这不是 detector FAIL。

## 尝试记录（2026-10-16）

- DeepSeek-V2-Lite TP2：aclnnAddRmsNormBias
- Moonlight-16B-A3B TP2：同样的 ACL 错误
- Qwen3-30B-A3B TP2 util 0.75：boot 中途 OOM kill

后来已有跑通归档；本文件只保留历史 setup 语境。
