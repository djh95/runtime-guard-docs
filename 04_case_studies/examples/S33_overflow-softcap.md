# 案例：Overflow / softcap 塌缩（PASS）

## 元信息
- **ID:** S33 · **Type:** Overflow·softcap · **Outcome:** 教学模版
- Guard pin: G2 · 协议: origin-faithful（见 `anomaly-PRINCIPLES.md`）
- 公开角色: **典型模版**（完整 runs/FE 在 test 仓库）

## 教学点
overflow/bang 类 L2 代表

## 现象
复读塌缩；`token_repeat`

## 三层率（归档）
`trigger / precision / detect` ≈ **132 / 15 / 48**

## Guard / skills 定界
- Online detect: 是 `token_repeat`
- Skills 到达: L2
- **非 L4**：不宣称定位到算子行 / commit

## 证据路径（test 仓库）
- Fail-evidence: `runtime-guard-test/tests/build-anomaly-env/fail-evidence/S33/`（`WHY_PASS.md` + `layers.json`）
- Skills run: `runtime-guard-test/docs/anomaly-skills-runs/S33-20261017.md`

## 备注
≠ S20 constructed softcap（证据在 test）。
