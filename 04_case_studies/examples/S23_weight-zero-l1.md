# 案例：权重置零 always-on（L1-only）

## 元信息
- **ID:** S23 · **Type:** Quant·weight · **Outcome:** 教学模版
- Guard pin: G2 · 协议: origin-faithful（见 `anomaly-PRINCIPLES.md`）
- 公开角色: **典型模版**（完整 runs/FE 在 test 仓库）

## 教学点
能检不能定界到权重元素；skills 停在 L1

## 现象
复读/`token_repeat`；无稳定 class→layer 叙事

## 三层率（归档）
`trigger / precision / detect` ≈ **2 / 17 / 48**

## Guard / skills 定界
- Online detect: 是 `token_repeat`
- Skills 到达: **L1 only**
- **非 L4**：不宣称定位到算子行 / commit

## 证据路径（test 仓库）
- Fail-evidence: `runtime-guard-test/tests/build-anomaly-env/fail-evidence/S23/`（`WHY_PASS.md` + `layers.json`）
- Skills run: `runtime-guard-test/docs/anomaly-skills-runs/S23-20261017.md`

## 备注
展示天花板：detect ≠ localization。
