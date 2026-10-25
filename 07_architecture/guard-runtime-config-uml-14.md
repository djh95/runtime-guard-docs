# Guard + runtime_config — UML 2 十四图

**Scope:** Runtime Guard（detect / report / dump）+ `runtime_config`（control plane）。  
**Sources:** 本仓 [01 如何启动](../01_enable_and_start/README.md)、上游 `runtime_guard` / `runtime_config` 源码与产品文档；符号清单见 `guard-uml-inventory-20261021`。  
**Wiring:** 主产品树仅 **MRV2**（`worker/v2/model_runner.py`）；**MRV1** 经本仓 [05_mrv1_backport](../05_mrv1_backport/README.md) 离线 patch（与 [05_v030](../05_v030_backport/README.md) MRV2 勿叠打）。

Mermaid 表达不了的类型（Profile / Timing / Communication 部分）用 **PlantUML-style / ASCII** 标注。

---

## 1. Class 类图

核心类型与继承/组合：`RuntimeConfigBootstrap` → `RuntimeConfig`；`RuntimeGuardProcessor` 组合 Bus/Dump/Report mixins 与 `DetectorManager`。

```mermaid
classDiagram
  direction TB

  class AscendConfig {
    +runtime_config RuntimeConfig
  }
  class build_runtime_config_from_additional
  class RuntimeConfigBootstrap {
    +path
    +hot_reload
    +runtime_config dict
  }
  class RuntimeConfig {
    +hot_reload_enabled
    +ensure_persisted()
    +is_fully_off()
    +needs_sample_phase_hooks()
    +config_due_local()
    +manual_trigger()
  }

  class RuntimeGuardProcessor {
    +bind(runner)
    +sync_for_step()
    +end_of_wave_sync()
    +run_sample_phase()
    +check_before_sample()
    +check_after_sample()
    +is_fully_off()
  }
  class RuntimeGuardBusMixin
  class RuntimeGuardDumpMixin
  class RuntimeGuardReportMixin
  class DetectorManager
  class TokenRepeatDetector
  class LogitsFiniteDetector
  class SpecAcceptanceDetector
  class AnomalyDetector
  class ConfigBackedDetector
  class DueBitsBusWorker
  class ActionExecutor
  class ReportWriter
  class RequestGuardStore
  class WaveTracker
  class DumpQuota
  class NPUModelRunner_v2

  build_runtime_config_from_additional ..> RuntimeConfigBootstrap : returns
  AscendConfig --> RuntimeConfig : owns
  RuntimeConfigBootstrap ..> RuntimeConfig : seeds
  RuntimeGuardProcessor --|> RuntimeGuardBusMixin
  RuntimeGuardProcessor --|> RuntimeGuardDumpMixin
  RuntimeGuardProcessor --|> RuntimeGuardReportMixin
  RuntimeGuardProcessor --> RuntimeConfig
  RuntimeGuardProcessor --> DetectorManager
  RuntimeGuardProcessor --> DueBitsBusWorker
  RuntimeGuardProcessor --> ActionExecutor
  RuntimeGuardProcessor --> ReportWriter
  RuntimeGuardProcessor --> RequestGuardStore
  RuntimeGuardProcessor --> WaveTracker
  RuntimeGuardProcessor --> DumpQuota
  DetectorManager --> TokenRepeatDetector
  DetectorManager --> LogitsFiniteDetector
  DetectorManager --> SpecAcceptanceDetector
  TokenRepeatDetector --|> ConfigBackedDetector
  LogitsFiniteDetector --|> ConfigBackedDetector
  SpecAcceptanceDetector --|> ConfigBackedDetector
  ConfigBackedDetector --|> AnomalyDetector
  NPUModelRunner_v2 --> RuntimeGuardProcessor : bind()
```

---

## 2. Object 对象图

某一 wave 上 last-PP 的典型实例快照（hot_reload 开、token_repeat 开）。

```mermaid
flowchart LR
  subgraph objs["object instances @ last-PP"]
    ac["ac: AscendConfig"]
    rc["rc: RuntimeConfig\nhot_reload=true\npath=/data/runtime/config/runtime_config.json"]
    rg["rg: RuntimeGuardProcessor"]
    dm["dm: DetectorManager"]
    tr["tr: TokenRepeatDetector\nenabled=true"]
    lf["lf: LogitsFiniteDetector\nenabled=false"]
    bus["bus: DueBitsBusWorker"]
    store["store: RequestGuardStore"]
    runner["runner: NPUModelRunner v2"]
  end
  ac -->|runtime_config| rc
  runner -->|runtime_guard| rg
  rg --> rc
  rg --> dm
  rg --> bus
  rg --> store
  dm --> tr
  dm --> lf
```

---

## 3. Component 组件图

部署边界上的可替换组件与产物目录。

```mermaid
flowchart TB
  subgraph startup["startup"]
    addcfg["additional_config\nruntime_* keys"]
    bootstrap["build_runtime_config_from_additional\n→ RuntimeConfigBootstrap"]
  end
  subgraph ctrl["ConfigControlPlane"]
    rcfile["runtime_config.json\nlive JSONC"]
    rtobj["RuntimeConfig"]
  end
  subgraph guard["GuardCore"]
    proc["RuntimeGuardProcessor\n+ Bus/Dump/Report mixins"]
    dets["Detectors\nTokenRepeat / LogitsFinite / SpecAcceptance"]
    busw["DueBitsBusWorker"]
  end
  subgraph engine["EngineAdapters"]
    mrv2["NPUModelRunner v2\n@runtime_guard_step\n@runtime_guard_sample_tokens"]
    worker["NPUWorker\n@runtime_guard_idle_step"]
  end
  subgraph disk["on-disk"]
    report["runtime_report_dir\nreport_*.json"]
    dump["runtime_dump_dir / kv_cache\n*.pt"]
  end
  addcfg --> bootstrap --> rtobj
  rcfile <-->|hot_reload / file poll| rtobj
  rtobj --> proc
  mrv2 --> proc
  worker --> proc
  proc --> dets
  proc --> busw
  proc -->|last-PP TP0| report
  proc -->|last-PP all TP| dump
```

---

## 4. Composite Structure 复合结构图

`RuntimeGuardProcessor` 内部端口：wave sync / sample phase / due bus。

```mermaid
flowchart TB
  subgraph RGP["RuntimeGuardProcessor"]
    direction TB
    p_sync[["port: sync_for_step / end_of_wave_sync"]]
    p_sample[["port: run_sample_phase\ncheck_before/after_sample"]]
    p_bus[["port: MergedBusRequest\nconfig_due + dump_due"]]
    busM["RuntimeGuardBusMixin"]
    dumpM["RuntimeGuardDumpMixin"]
    reportM["RuntimeGuardReportMixin"]
    dm["DetectorManager"]
    aq["ActionExecutor + ActionQueue"]
    p_sync --- busM
    p_sample --- dm
    p_bus --- busM
    dm --> aq
    aq --> reportM
    aq --> dumpM
  end
  runner["NPUModelRunner v2 hooks"] -->|wave| p_sync
  runner -->|sample| p_sample
  tpPeers["last-PP sibling TP"] <-->|due bus| p_bus
```

---

## 5. Deployment 部署图

多 rank 节点：last-PP TP0 写 report；同 stage 其它 TP 经 due bus；非 last-PP file poll。

```mermaid
flowchart TB
  subgraph node0["NPU node / last PP"]
    tp0["TP0 worker\nRuntimeGuardProcessor\ndetect + ReportWriter"]
    tp1["TP1 worker\nDueBitsBusWorker peer\nKV shard only"]
    json["shared: runtime_config.json"]
    rep["PVC: runtime_report_dir"]
    kv["local/PVC: dump_dir"]
  end
  subgraph node1["earlier PP / API"]
    pp0["non-last-PP worker\nfile poll only"]
  end
  json -.->|hot_reload read| tp0
  tp0 <-->|due bus\nconfig_due dump_due| tp1
  tp0 -->|report_*.json| rep
  tp0 -->|dp*_tp0_*.pt| kv
  tp1 -->|dp*_tp1_*.pt| kv
  json -.->|file poll| pp0
```

---

## 6. Package 包图

与清单建议的五包划分一致。

```mermaid
flowchart LR
  subgraph ConfigControlPlane
    rc_pkg["runtime_config\nRuntimeConfig\nRuntimeConfigBootstrap\nschema / detector_catalog\n_defaults / dist"]
    ascend["ascend_config\ninit_ascend_config"]
  end
  subgraph GuardCore
    rg_pkg["runtime_guard\nprocessor + mixins\nstate / io / rank_gate"]
  end
  subgraph Detectors
    det_pkg["detector/\nTokenRepeatDetector\nLogitsFiniteDetector\nSpecAcceptanceDetector\nDetectorManager"]
  end
  subgraph ActionsIO
    act_pkg["action/ + report + dump\nDueBitsBusWorker"]
  end
  subgraph EngineAdapters
    hooks["hooks.py\nruntime_guard_step\nruntime_guard_sample_tokens\nruntime_guard_idle_step"]
    mrv2["worker/v2/model_runner.py"]
    wk["worker/worker.py"]
    mrv1["«MRV1 backport»\nmodel_runner_v1.py"]
  end
  ascend --> rc_pkg
  rc_pkg --> GuardCore
  GuardCore --> Detectors
  GuardCore --> ActionsIO
  EngineAdapters --> GuardCore
```

---

## 7. Profile 概要图（轻量 stereotypes）

Mermaid 无原生 Profile；下列为 **PlantUML-style** stereotypes（扩展点，非正式 metamodel）。

```plantuml
@startuml
skinparam packageStyle rectangle
profile RuntimeGuardProfile {

  stereotype «ControlPlane» {
    RuntimeConfig, RuntimeConfigBootstrap
  }
  stereotype «Detector» {
    TokenRepeatDetector, LogitsFiniteDetector, SpecAcceptanceDetector
  }
  stereotype «Action» {
    ReportAction, DumpKvAction
  }
  stereotype «RankGate» {
    lastPP_TP0_detect_report
    lastPP_allTP_dump
    nonLastPP_file_poll
  }
  stereotype «EngineHook» {
    runtime_guard_step
    runtime_guard_sample_tokens
    runtime_guard_idle_step
  }
  stereotype «MRV1Only» {
    runtime_guard_pre_sample_logits
    build_v1_async_gpu_output
  }
  stereotype «IdleMode» {
    static_idle = is_fully_off()
    worker_idle = execute_dummy_batch + idle_step
  }
}
@enduml
```

---

## 8. Use Case 用例图

运维与引擎两侧主要用例。

```mermaid
flowchart LR
  ops((User / ops))
  eng((vLLM EngineCore))
  npu((NPU worker))

  subgraph system["Runtime Guard"]
    uc1([启服注入 additional_config])
    uc2([热更 live JSON / manual_dump 水位])
    uc3([wave sync + due bus])
    uc4([检出 token_repeat / logits_finite / spec_acceptance])
    uc5([写 report JSON last-PP TP0])
    uc6([dump KV last-PP all TP])
    uc7([static idle 旁路])
  end

  ops --> uc1
  ops --> uc2
  ops --> uc5
  ops --> uc6
  eng --> uc3
  eng --> uc4
  npu --> uc3
  npu --> uc7
  uc4 --> uc5
  uc4 --> uc6
```

---

## 9. Activity 活动图

从 `additional_config` 到 hit → report/dump。

```mermaid
flowchart TD
  A[additional_config.runtime_*] --> B[build_runtime_config_from_additional]
  B --> C[RuntimeConfigBootstrap → AscendConfig.runtime_config]
  C --> D[NPUModelRunner v2 __init__\nRuntimeGuardProcessor.bind]
  D --> E{is_fully_off?\nstatic idle}
  E -->|yes| F[bare execute_model / sample_tokens]
  E -->|no| G[runtime_guard_step: sync_for_step]
  G --> H[forward]
  H --> I[runtime_guard_sample_tokens]
  I --> J[check_before_sample logits_finite]
  J --> K[sample body]
  K --> L[run_sample_phase\ncheck_after_sample / after_spec]
  L --> M{Incident?}
  M -->|no| N[end_of_wave_sync / drain bus]
  M -->|yes| O[ActionQueue: report / dump_kv]
  O --> P[ReportWriter TP0 + KvCacheReader all TP]
  P --> N
```

---

## 10. State Machine 状态机

进程级 Guard 热路径门控（`RuntimeConfig` / `is_fully_off`）。

```mermaid
stateDiagram-v2
  [*] --> StaticIdle: detectors+dump+hot_reload all off
  StaticIdle --> Armed: enable detector or dump or hot_reload
  Armed --> ConfigDue: hot_reload mtime/digest change
  ConfigDue --> Armed: apply cascade / due bus config_due
  Armed --> Detecting: needs_sample_phase_hooks wave
  Detecting --> ActionPending: Incident
  ActionPending --> Dumping: dump_kv armed
  ActionPending --> Reporting: report on last-PP TP0
  Dumping --> Armed: end-of-wave D2H done
  Reporting --> Armed: report written
  Detecting --> Armed: no hit
  Armed --> StaticIdle: hot-reload turns all gates off
  Armed --> WorkerIdleSync: DP idle dummy_batch
  WorkerIdleSync --> Armed: sync_for_step no tokens
```

---

## 11. Sequence 序列图

busy wave：step → sample → due bus drain。

```mermaid
sequenceDiagram
  participant Eng as EngineCore
  participant MR as NPUModelRunner v2
  participant Hook as hooks
  participant RG as RuntimeGuardProcessor
  participant RC as RuntimeConfig
  participant Bus as DueBitsBusWorker
  participant Det as DetectorManager
  participant Act as ActionExecutor

  Eng->>MR: execute_model(scheduler_output)
  MR->>Hook: runtime_guard_step
  Hook->>RG: sync_for_step
  RG->>RC: refresh / config_due_local
  RG->>Bus: submit MergedBusRequest(config_due, dump_due)
  Hook->>MR: forward body
  Eng->>MR: sample_tokens
  MR->>Hook: runtime_guard_sample_tokens
  Hook->>RG: check_before_sample (logits_finite)
  Hook->>MR: sample body
  Hook->>RG: run_sample_phase / check_after_sample (token_repeat)
  alt Incident
    RG->>Act: enqueue report + dump_kv
    Note over Act: report = last-PP TP0<br/>dump = last-PP all TP
  end
  Hook->>RG: end_of_wave_sync / drain bus
  Bus-->>RG: MergedBusResult → sibling TP
```

---

## 12. Communication 通信图

Mermaid 无原生 communication diagram；下列为 **编号消息协作图**（UML Communication）。

```text
                    (1) sync_for_step
  EngineCore ---------------------> RuntimeGuardProcessor
                                          |
                         (2) submit due bus | (5) check_after_sample
                                          v
                                   DueBitsBusWorker
                                          |
                         (3) broadcast[wave, config_due, dump_due]
                                          v
                               last-PP TP1..TPn  ----(4) local KV shard----> dump_dir

  RuntimeGuardProcessor --(6) ReportAction--> ReportWriter --(7)--> runtime_report_dir
  RuntimeGuardProcessor --(8) DumpKvAction--> KvCacheReader --(9)--> dump_dir

  Non-last-PP / API --(F) file poll--> runtime_config.json
  Ops --(0) edit JSON / raise manual_dump--> runtime_config.json
```

```mermaid
flowchart TB
  Eng[EngineCore] -->|1 sync| RG[RuntimeGuardProcessor]
  RG -->|2 submit| Bus[DueBitsBusWorker]
  Bus -->|3 bcast| TPn[last-PP TP peers]
  RG -->|5 detect| Det[DetectorManager]
  Det -->|6 alert| RG
  RG -->|7 report| RW[ReportWriter TP0]
  RG -->|8 dump| KV[KvCacheReader all TP]
  Ops[Ops] -->|0 edit| JSON[runtime_config.json]
  JSON -.->|F poll| NonPP[non-last-PP]
  JSON -->|hot path| RG
```

---

## 13. Timing 时间图

Wave 内 due-bus 与 forward 重叠；async after-sample 可能晚于 finish。  
（Mermaid **gantt** 近似 UML Timing。）

```mermaid
gantt
  title last-PP wave timing (schematic)
  dateFormat X
  axisFormat %s
  section TP0
  sync_for_step + due-bus submit     :a1, 0, 1
  forward compute                     :a2, 1, 5
  sample + logits_finite / token_repeat :a3, 5, 7
  end_of_wave drain bus + dump D2H    :a4, 7, 9
  section TP peer
  due-bus collective wait/overlap     :b1, 0, 5
  apply config_due / dump_due         :b2, 7, 8
  write local *.pt                    :b3, 8, 9
  section async
  AscendAsyncOutput.get_output after-sample :c1, 8, 10
```

```text
time →
TP0:   |--sync+submit--|-- forward --|-- sample/detect --|-- drain/D2H --|
peer:  |<<<< due bus overlap >>>>>>>>|---- apply due ----|-- .pt write --|
async:                                            |---- get_output drain ----|
static idle: bare runner (no sync shells)
worker idle: idle_step sync only (no scheduled tokens)
```

---

## 14. Interaction Overview 交互概览图

活动图骨架 + 嵌入交互引用（ref）。

```mermaid
flowchart TD
  start([start serve / LLM]) --> boot[ref: bootstrap\nbuild_runtime_config_from_additional\n+ RuntimeGuardProcessor.bind]
  boot --> gate{static idle?\nis_fully_off}
  gate -->|yes| bare[ref: bare MRV2 methods]
  gate -->|no| wave[ref: Sequence §11\nstep + sample + due bus]
  wave --> hit{Incident / manual_dump?}
  hit -->|yes| io[ref: Communication §12\nreport TP0 + dump all TP]
  hit -->|no| eow[end_of_wave_sync]
  io --> eow
  eow --> more{more waves?}
  bare --> more
  more -->|yes| gate
  more -->|no| stop([shutdown])
```

---

## 相关链接

| 文档 | 路径 |
|------|------|
| 启停 | [01_enable_and_start](../01_enable_and_start/README.md) |
| MRV1 接线 | [05_mrv1_backport](../05_mrv1_backport/README.md) |
| MRV2 v0.30 | [05_v030_backport](../05_v030_backport/README.md) |
| 上游 feature | `vllm-ascend` `docs/.../runtime_guard.md` |
| 上游 JSON | `vllm-ascend` `docs/.../runtime_config.md` |
