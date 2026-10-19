# 案例：FullAttn recycle-zero（PASS）

## 元信息
- **ID:** S10′ · **Type:** KV·PD·pad · **Outcome:** 教学模版
- Guard pin: G2 · 协议: origin-faithful（见 `anomaly-PRINCIPLES.md`）
- 公开角色: **典型模版**（完整 runs/FE 在 test 仓库）

## 教学点
KV recycle 未清零 → 复读塌缩；skills 可达 L2（L3 潜力）

## 现象
短语/复读塌缩；`token_repeat`

## 三层率（归档）
`trigger / precision / detect` ≈ **65 / 20 / 79**

## Guard / skills 定界
- Online detect: 是 `token_repeat`
- Skills 到达: L2–L3 潜力
- **非 L4**：不宣称定位到算子行 / commit

## 证据路径（test 仓库）
- Fail-evidence: `runtime-guard-test/tests/build-anomaly-env/fail-evidence/S10/`（`WHY_PASS.md` + `layers.json`）
- Skills run: 无独立 `Sxx-*.md` → 见 `runtime-guard-test/docs/anomaly-skills-runs/batch-pass-wave-20261017.md`

## 备注
目录名用 `S10/`（prime）；公开文件名 `S10p_*.md`。无独立 run 文件 → 见 batch-pass-wave。与 **S01 GAP** 对照。
