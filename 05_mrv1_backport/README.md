# ⑤ 支持 MRV1 — 多 release Guard 接线

给**无 Runtime Guard**（或仅有 V2 接线）的历史 / 常用 release 打上 **Model Runner V1** 接线，使旧树能出 detect / report / `dump_kv`。

| 线 | 目录 | Skill | 含义 |
|----|------|-------|------|
| **支持 MRV1** | 本目录 `05_mrv1_backport/` | `apply-mrv1-patch` | 多 release × **MRV1** |
| **支持 0.30 MRV2** | [`05_v030_backport/`](../05_v030_backport/) | `apply-v030-mrv2-patch` | **仅** v0.30 × **MRV2** |

**v0.30 两条线并存：** 本目录 `v0.30.0/` = MRV1；`05_v030_backport` = MRV2。同一 BASE 上二选一打，不要叠打。

## 何时用

| 你的版本 | 怎么做 |
|----------|--------|
| 下表「已适配」release，且跑 **Model Runner V1** | checkout 对应 **BASE** → 本目录 `apply_patch.sh --release …` |
| `releases/v0.30.0` 且跑 **MRV2** | 用 [`05_v030_backport`](../05_v030_backport/)，**不要**打本目录的 `v0.30.0` |
| 更早 / 未列出 | README「未适配」；勿硬套 |

当前包版本与 BASE 见 **[CHANGELOG.md](./CHANGELOG.md)**。

## 接线包 ≠ anomaly pin

- 本包 = **Guard 控制面 + MRV1 接线**（对照源：`feat/runtime-guard-config-v1` @ `9343c9859` + 各 release BASE 适配）。
- **不含** anomaly overlay；**不含** main G2 / `#18644` 鲁棒全集（与 `05_v030` 一致：接线包与 anomaly pin `f2aefd068…` 分开）。

## 第一期已适配（5 档）

| Release 目录 | 上游 ref | BASE（短） | 说明 |
|--------------|----------|------------|------|
| `v0.23.0` | tag `v0.23.0` | `5cb98caaa` | 主档；**`v0.23.0.post1` 同包可 apply**（已 `--check`） |
| `v0.26.0rc1` | tag `v0.26.0rc1` | `f2f74a16c` | |
| `v0.27.1rc1` | tag `v0.27.1rc1` | `3b3188623` | |
| `v0.28.0rc1` | tag **`v0.28.0.rc1`**（点号） | `96df62310` | 目录名无点；checkout 用带点 tag |
| `v0.30.0` | 与 `05_v030` **同一 BASE** `6d25ba2b3` | `6d25ba2b3` | **只接 MRV1**；MRV2 走 `05_v030` |

未适配（本期不做）：`v0.18.0`、v0.13 及更早。

## 使用

```bash
git clone https://github.com/vllm-project/vllm-ascend.git
cd vllm-ascend
git checkout <BASE>   # 见 CHANGELOG / 各 <release>/BASE.md

bash /path/to/runtime-guard-docs/05_mrv1_backport/apply_patch.sh \
  --release v0.23.0 "$(pwd)"
# 或自动探测 tag/分支名：
# bash .../apply_patch.sh "$(pwd)"
```

冲突时脚本停住——反馈 `git status`，勿 `--reject` 当生产用。

## 相关

- 0.30 MRV2：[../05_v030_backport/README.md](../05_v030_backport/README.md)  
- 启动：[../01_enable_and_start/README.md](../01_enable_and_start/README.md)  
- Skills：`apply-mrv1-patch` / `apply-v030-mrv2-patch`（[`06_agent_skills/`](../06_agent_skills/)）  
