# 案例：top-k on `-logits` → unique garbage（GAP）

## 元信息
- **ID:** S45 · **Type:** Embed·logits·sampler · **Outcome:** 教学模版
- Guard pin: G2 · 协议: origin-faithful（见 `anomaly-PRINCIPLES.md`）
- 公开角色: **典型模版**（完整 runs/FE 在 test 仓库）

## 教学点
第三种漏检：unique 垃圾；identical-mode 低估 precision

## 现象
每请求不同乱码；`token_repeat`/`logits_finite` 双漏

## 三层率（归档）
`trigger / precision / detect` ≈ **16 / 0 / **0****

## Guard / skills 定界
- Online detect: 否（GAP）
- Skills 到达: 弱 L2（samples）
- **非 L4**：不宣称定位到算子行 / commit

## 证据路径（test 仓库）
- Fail-evidence: `runtime-guard-test/tests/build-anomaly-env/fail-evidence/S45/`（`WHY_UNDETECTED.md` + `layers.json`）
- Skills run: `runtime-guard-test/docs/anomaly-skills-runs/S45-20261017.md`

## 备注
与 **S43 PASS** 对照（同 sampler/embed 族）。
