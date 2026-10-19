# ① 如何启动 Runtime Guard

适用：开发联调、业务启服、一线临时开观测。  
前置：**Model Runner v2**（v1 未接线）。  
默认 detector / hot-reload / dump **全关**，进入 **static idle** 热路径旁路（[#18644](https://github.com/vllm-project/vllm-ascend/pull/18644) 优化），开销可忽略；开启 detector、dump、热更能力后会引入额外 CPU 开销（功能来自 [#16849](https://github.com/vllm-project/vllm-ascend/pull/16849)），性能敏感业务建议评估后启用。

## 相关上游文档

| 说明 | URL |
|------|-----|
| 功能说明 | https://github.com/vllm-project/vllm-ascend/blob/main/docs/source/user_guide/feature_guide/runtime_guard.md |
| 配置字段 | https://github.com/vllm-project/vllm-ascend/blob/main/docs/source/user_guide/configuration/runtime_config.md |
| additional_config | https://github.com/vllm-project/vllm-ascend/blob/main/docs/source/user_guide/configuration/additional_config.md#runtime_guard |

**版本支持：**

- **到 release `0.30.0`（含）一律不支持** Runtime Guard，须先打本手册 [05_v030_backport](../05_v030_backport/README.md) 的 patch，再按本文启动。
- **更晚的版本**：先打开上面三个链接，把 URL 里的 `main` 换成你的 **tag / 分支**（例如 `v0.31.0`）。若文档 404 或源码中没有 `runtime_guard`，同样先打 [05 patch](../05_v030_backport/README.md)（或该版本对应的后续 patch 包），再启动。

---

## 1. 启动参数（`--additional-config`）

| Key | 类型 | 含义 |
|-----|------|------|
| `runtime_config_path` | str | live JSON 路径；默认 `<cwd>/runtime/config/runtime_config.json` |
| `runtime_config_hot_reload` | bool | **仅启动参数**；`true` 才允许启动后改 JSON 生效 |
| `runtime_config` | dict | 启动 overlay，合并进默认后 **覆盖写** 到 path |
| `runtime_report_dir` | str | 报告根；默认 `<cwd>/runtime/report` |
| `runtime_dump_dir` | str | 种子 `dump.dump_dir`；之后 JSON 热更可改 |

**重要：** worker leader 每次启动会按「默认 ← overlay」**覆盖写** JSON。需要热更时：**先启动，再改文件**。

---

## 2. 三种常用启法

### A. 生产基线（推荐默认）

不加任何 `runtime_*`。全关；需要时再开 B/C。

### B. 启动时固定打开（不热更）

```bash
vllm serve <MODEL> --additional-config '{
  "runtime_config": {
    "detector": {
      "token_repeat": { "enabled": true, "on_trigger": ["report"] },
      "logits_finite": { "enabled": true }
    }
  }
}'
```

- `hot_reload` 默认 `false` → 启动后改 JSON **无效**，改策略需重启。  
- 适合：策略稳定、不想被人热改。

### C. 值班 / 排障（热更新）

```bash
vllm serve <MODEL> --additional-config '{
  "runtime_config_path": "/data/runtime/config/runtime_config.json",
  "runtime_config_hot_reload": true,
  "runtime_report_dir": "/data/runtime/report",
  "runtime_dump_dir": "/data/runtime/kv_cache"
}'
```

启动后编辑 live JSON（支持 JSONC：注释、尾逗号）。路径请用**绝对路径**（容器 / systemd 下 cwd 常变）。

**命中并 dump 的最小热更片段：**

```json
{
  "dump": { "auto_max_times": 3, "auto_cooldown_seconds": 300 },
  "detector": {
    "token_repeat": {
      "enabled": true,
      "on_trigger": ["report", "dump_kv"]
    }
  }
}
```

**Manual dump（水位，不是剩余次数）：**

- JSON 里 `dump.manual_dump = N` 是 **目标水位**；进程**从不写回** `false`/`0`。  
- 进程内 `done`（已拍次数）只在**内存**；当 `done ≥ N` 就停。  
- 再拍一次：热更把 N **抬高**（推荐 `1` → `2` → `3`），勿一次设很大的 `N`。  
- 需要 `runtime_config_hot_reload=true`。

---

## 3. 落盘布局

```text
runtime/
  config/runtime_config.json
  report/
    <incident_type>/report_*.json          # 仅 last-PP TP0
    kv_cache/<type>/<req_id>/wave_*/
      request_info.json
      dp*_tp*_pp*_cp*/*.pt                 # last-PP × 各 TP
```

| 产物 | 谁写 |
|------|------|
| Report JSON | last-PP **TP0** |
| KV `.pt` | last-PP **全部 TP** |
| 非 last PP | 不参与 dump bus；报告不在这些 rank 上找 |

---

## 4. 不同部署要注意什么

| 场景 | 注意 |
|------|------|
| 单卡 | 绝对路径；默认关时为 static idle（见开篇） |
| TP>1 | 检测/报告只在 last-PP TP0；dump 要凑齐各 `tp*` |
| PP>1 | sync/dump 只在 last PP；别在早期 PP 找报告 |
| DP>1 | 各副本独立报告/dump；共享 JSON 时内存 `done` 每进程独立（盘上水位 `N` 共享、不写回） |
| 多机 | 可启动后改路径，但 **last-PP 的 TP 组要统一改**；除 TP0 外其他 rank **不读配置文件**（见附录） |
| MoE | 开功能后 Python 占比更明显；默认关即可 |
| Spec / MTP | 才需要 `spec_acceptance` |
| Async scheduling | after-sample 在 `AscendAsyncOutput.get_output()`；finish 可能早于 dump |
| 容器 / K8s | 持久卷 + 绝对路径；按 Pod 分子目录，防互相覆盖（见附录） |
| Offline `LLM()` | Python 离线 API（对比 `vllm serve`）；同样用 `additional_config` 注入；须 v2 runner（见附录） |

检测器细节见 [03_detectors](../03_detectors/README.md)。更细的拓扑白话见下方 **附录**。

---

## 5. 启服后自检

1. 日志出现 `[runtime_config]` / interaction mode / `hot_reload=...`。  
2. 发一笔可触发请求 → `runtime_report_dir` 下是否有 JSON（last-PP TP0）。  
3. 若开了 `dump_kv`：`kv_cache/.../wave_*/dp*_tp*_pp*_cp*/*.pt` 是否 TP 齐全。  
4. `report.max_per_req`（默认 1）达上限后该 req **停止检测**。

---

## 6. 常见误区

1. 启动前改 JSON → 被 overwrite。  
2. `hot_reload=false` 却改 live JSON → 无效。  
3. 在非 last PP / 非 TP0 找 report。  
4. 只用某一个 `tp*` 的 `.pt` 当完整 KV。  
5. v1 runner → Guard 未接线。  
6. `≤0.30.0`（或更新版本仍无 Guard）却直接配 `runtime_*` → 参数被忽略或报错；先打 [05 patch](../05_v030_backport/README.md)。  
7. 再拍需热更抬高水位 `N`（JSON 里的 `manual_dump` 不会被进程改掉）。

---

## 7. 下一步

- 要排障定界 → [02 问题定位分析](../02_problem_localization/README.md)  
- 要调阈值/阈值 → [03 检测算法](../03_detectors/README.md)

---

## 附录 A. 部署注意（白话补强）

### A.1 术语速记

| 词 | 意思 |
|----|------|
| last-PP TP0 | 流水线**最后一段**里的 **0 号**张量并行卡：只在这里跑检测、写 report |
| `tp*` dump | last-PP 上每个 TP 各写一份 KV 分片；要凑齐才能拼完整 |
| static idle | detector/dump/热更全关时的旁路，开销可忽略 |
| `manual_dump=N` / `done` | 盘上水位目标 vs 进程内存已拍次数；**JSON 不写回** |

### A.2 多机

跨节点跑 TP/PP/DP 时，每台机器仍按路径读写文件。

- **可以启动后再改** report/dump/config 路径（热更），但 **last-PP 这一组里的所有 TP 必须改成同一套路径约定**（同构绝对路径，或同一共享盘挂载点）。只改 TP0、其它 TP 还指旧盘 → dump 会缺 `tp1`/`tp2`…  
- **除 TP0 外，其它 rank 默认不读 live 配置文件做决策**：检测与写 report 只在 last-PP TP0；其它 TP 主要跟着 dump/同步总线写自己的分片。改配置时盯 **TP0 能读到的那份 JSON**，并保证 dump 目录对各 TP 都可写。  
- dump `.pt` 又多又大：**优先本机本地盘**；NFS 更适合放 config/小报告（注意延迟）。

### A.3 容器 / K8s（白话）

容器里的「当前目录」经常变，重启后本地盘可能清空。

1. **挂卷（PVC/hostPath）**：把 `/data/runtime` 之类挂到宿主机或共享存储，否则 report/dump 丢。  
2. **绝对路径**：配置写成 `/data/runtime/config/runtime_config.json`，不要靠相对路径。  
3. **按 Pod 分子目录**：多副本若共用同一挂载根，会互相覆盖。用  
   `/data/runtime/pod-a/report`、`/data/runtime/pod-b/report`（或带 hostname/pod UID）。  
4. 热更时确认：**这个 Pod 的进程**读的是它自己那份 JSON。

### A.4 Offline `LLM()` 是什么？

| 方式 | 是什么 |
|------|--------|
| **`vllm serve`** | 起 HTTP 服务，外部用 API 请求 |
| **Offline `LLM()`** | 在 Python 里 `from vllm import LLM`（或 Ascend 等价入口）**进程内**直接 `generate`，不对外开服务 |

两者启用 Guard 的开关入口相同：都通过 **`additional_config`**（以及其中的 `runtime_config_*` / `runtime_config`）注入，**不是另一套独立开关**。  
仍然必须是 **Model Runner v2**；v1 未接线，配了也不会出 report。`≤0.30.0` 先打 [05 patch](../05_v030_backport/README.md)。

### A.5 其它拓扑一行版

- **TP>1**：报告只看 TP0；dump 检查是否凑齐各 `tp*`。  
- **PP>1**：只在最后一段找报告/dump；更早 PP 没有是预期。  
- **DP>1**：各副本各写各的；共享水位 `N` 时每人内存 `done` 独立 → 大约可拍 `num_DP×N` 次。  
- **MoE**：默认关；开观测后 host CPU 更显眼。  
- **Spec/MTP**：才开 `spec_acceptance`。  
- **Async**：检测挂在 `AscendAsyncOutput.get_output()`；业务 finish 可能早于 dump 落盘。
