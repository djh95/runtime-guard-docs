# 案例：W8A8 scale collapse（GAP）

## 元信息
- **ID:** S07 · **Type:** Quant·weight · **Outcome:** 教学模版
- Guard pin: G2 · 协议: origin-faithful（见 `anomaly-PRINCIPLES.md`）
- 公开角色: **典型模版**（完整 runs/FE 在 test 仓库）

## 教学点
量化 scale 塌缩 → 有限垃圾；与 S01 同缺口、不同根因

## 现象
相同/混合有限垃圾；非复读窗

## 三层率（归档）
`trigger / precision / detect` ≈ **2624 / 1 / **0****

## Guard / skills 定界
- Online detect: 否（GAP）
- Skills 到达: 弱 L2（samples）
- **非 L4**：不宣称定位到算子行 / commit

## 证据路径（test 仓库）
- Fail-evidence: `runtime-guard-test/tests/build-anomaly-env/fail-evidence/S07/`（`WHY_UNDETECTED.md` + `layers.json`）
- Skills run: `runtime-guard-test/docs/anomaly-skills-runs/S07-20261017.md`

## 备注
≠ S23/S24（那些是 detect-only PASS）。优先补 garbled detector。
